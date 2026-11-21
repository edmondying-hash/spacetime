#!/usr/bin/env python3
"""
TARGET E (CONTROL): Cubic-3D SU(2) reference for the 0++ glueball ratio
(`bcc/bcc_cubic_control.py`).

Question (preregistered, PREREGISTRATION.md item 7, Target E): Target D found
m_0++/sqrt(sigma) plateauing at ~5.5 on the BCC lattice, ~55% ABOVE the 4D
continuum SU(2) value (3.55 +- 0.15). The BCC gauge sector is a 3D SU(2) gauge
theory (spatial lattice, spatial plaquettes), so the correct comparison may be
the 3D continuum ratio. This control runs the SAME protocol on the standard
3D cubic SU(2) lattice:

  * 3 link directions, 12 plaquettes per site, beta = 2.15 (same Wilson
    coupling convention as the BCC code).
  * Parallel single-proposal Metropolis sweeps, step 0.45 (identical kernel
    family to Target D).
  * L in {8, 12, 16, 20}, 2000 therm + 3000 meas, seed = 3000 + L.
  * APE alpha = 0.55 x 3, 2x2 blocked plaquette 0++ operator, connected
    C(dt) at dt = 0..5, m = -ln(C(1)/C(0)), bootstrap B = 2000.

Decision fork (preregistered):
  (i)  ratio_cubic(L=20) == ratio_BCC(L=20) within ~2 combined errors
       -> the ~5.5 plateau is lattice-universal 3D SU(2) physics; the paper's
          reference must be the 3D continuum ratio, not 3.55 (4D).
  (ii) the two differ beyond ~2 combined errors
       -> BCC diagonal geometry shifts the ratio; the theory must explain
          the BCC-specific value.

No new knobs; bcc_config.py is not modified.
"""

import json
import math
import os
import time
from typing import Any, Dict, List

import numpy as np

from bcc_confinement_wilson import BCCPlaquetteMonteCarlo
from bcc_glueball_scaling import APE_ALPHA, APE_STEPS, B_BOOTSTRAP, MEAS_SWEEPS, STEP_PARAM, THERM_SWEEPS

BETA = 2.15
LATTICES: List[int] = [8, 12, 16, 20]


class CubicPlaquetteMonteCarlo(BCCPlaquetteMonteCarlo):
    """Standard 3D cubic SU(2) gauge field (3 link directions, 12 plaquettes/site)."""

    FWD_DIRS = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

    def __init__(self, lattice_size: int = 8, seed: int = 3008):
        super().__init__(lattice_size=lattice_size, seed=seed)
        self.planes = [(i, j) for i in range(3) for j in range(i + 1, 3)]

    def _staple_sum_su2(self, links: np.ndarray, mu: int) -> np.ndarray:
        """Cubic 3D staple: two plaquettes per (mu, nu) plane pair."""
        d_mu = self.FWD_DIRS[mu]
        u_mu = links[mu]
        staple = np.zeros_like(u_mu)
        for nu in range(3):
            if nu == mu:
                continue
            d_nu = self.FWD_DIRS[nu]
            u_nu = links[nu]
            # T+ = U_nu(x+mu) U_mu(x+nu)† U_nu(x)†
            staple += self._su2_mul(
                self._su2_mul(self._shift(u_nu, d_mu, 1), self._su2_dag(self._shift(u_mu, d_nu, 1))),
                self._su2_dag(u_nu),
            )
            # T- = U_nu(x-nu+mu)† U_mu(x-nu)† U_nu(x-nu)
            u_nu_mnu = self._shift(u_nu, d_nu, -1)
            staple += self._su2_mul(
                self._su2_mul(
                    self._su2_dag(self._shift(u_nu_mnu, d_mu, 1)),
                    self._su2_dag(self._shift(u_mu, d_nu, -1)),
                ),
                u_nu_mnu,
            )
        return staple


def vectorized_sweep_cubic(mc: CubicPlaquetteMonteCarlo, links: np.ndarray, beta: float) -> None:
    """One parallel Metropolis sweep (3 directions); same quaternion acceptance as Target D."""
    L = mc.L
    for mu in range(3):
        staple = mc._staple_sum_su2(links, mu)
        u = links[mu]
        v = mc.rng.normal(0.0, STEP_PARAM, size=(L, L, L, 3))
        norm = np.linalg.norm(v, axis=-1)
        nz = norm > 1e-12
        sin_over_n = np.zeros_like(norm)
        sin_over_n[nz] = np.sin(norm[nz]) / norm[nz]
        cos_n = np.ones_like(norm)
        cos_n[nz] = np.cos(norm[nz])
        step_q = np.empty((L, L, L, 4), dtype=np.float64)
        step_q[..., 0] = cos_n
        step_q[..., 1] = v[..., 0] * sin_over_n
        step_q[..., 2] = v[..., 1] * sin_over_n
        step_q[..., 3] = v[..., 2] * sin_over_n
        cand = mc._su2_mul(step_q, u)
        d = cand - u
        d_tr = d[..., 0] * staple[..., 0] - d[..., 1] * staple[..., 1] \
               - d[..., 2] * staple[..., 2] - d[..., 3] * staple[..., 3]
        acc = (d_tr >= 0.0) | (mc.rng.random((L, L, L)) < np.exp(np.clip(beta * d_tr, -700.0, 0.0)))
        links[mu] = np.where(acc[..., None], cand, u)


def _ape_smear_cubic(mc: CubicPlaquetteMonteCarlo, links: np.ndarray,
                     alpha: float = APE_ALPHA, steps: int = APE_STEPS) -> np.ndarray:
    """APE smearing for the cubic 3D lattice.

    Each cubic link has 4 neighboring plaquettes (2 per other direction), so the
    staple is normalized by 4 — the 3D analogue of the BCC code's /6.
    """
    u = links.copy()
    ndir = len(mc.FWD_DIRS)
    for _ in range(steps):
        u_next = np.zeros_like(u)
        for mu in range(ndir):
            st = mc._staple_sum_su2(u, mu)
            comb = (1.0 - alpha) * u[mu] + (alpha / 4.0) * st
            norm = np.linalg.norm(comb, axis=-1, keepdims=True)
            u_next[mu] = comb / np.maximum(1e-12, norm)
        u = u_next
    return u


def measure_o_z_cubic(mc: CubicPlaquetteMonteCarlo, links: np.ndarray) -> np.ndarray:
    """APE-smear and build the 2x2 blocked plaquette 0++ operator o(z) (3 planes)."""
    u_sm = _ape_smear_cubic(mc, links)
    p_field = np.zeros((mc.L, mc.L, mc.L), dtype=np.float64)
    for mu, nu in mc.planes:
        d_mu, d_nu = mc.FWD_DIRS[mu], mc.FWD_DIRS[nu]
        p_mu2 = mc._su2_mul(u_sm[mu], mc._shift(u_sm[mu], d_mu, 1))
        p_nu2 = mc._su2_mul(u_sm[nu], mc._shift(u_sm[nu], d_nu, 1))
        loop22 = mc._su2_mul(
            mc._su2_mul(p_mu2, mc._shift(p_nu2, d_mu, 2)),
            mc._su2_mul(mc._su2_dag(mc._shift(p_mu2, d_nu, 2)), mc._su2_dag(p_nu2)),
        )
        p_field += loop22[..., 0] / 3.0
    return np.mean(p_field, axis=(0, 1))


def run_one_lattice(L: int, seed: int) -> Dict[str, Any]:
    mc = CubicPlaquetteMonteCarlo(lattice_size=L, seed=seed)
    links = np.zeros((3, L, L, L, 4), dtype=np.float64)
    links[..., 0] = 1.0

    o_series = np.empty((MEAS_SWEEPS, L), dtype=np.float64)
    w_acc: Dict[str, List[float]] = {k: [] for k in ("1x1", "2x1", "1x2", "2x2")}

    t0 = time.time()
    for sweep in range(THERM_SWEEPS + MEAS_SWEEPS):
        vectorized_sweep_cubic(mc, links, BETA)
        if sweep >= THERM_SWEEPS:
            i = sweep - THERM_SWEEPS
            w_now = mc.measure_wilson_loops_su2(links, max_r=2)
            for k in w_acc:
                w_acc[k].append(w_now[k])
            o_series[i] = measure_o_z_cubic(mc, links)
    wall = time.time() - t0

    vac_mean = float(o_series.mean())
    fluct = o_series - vac_mean
    c_dt = [float(np.mean(fluct * np.roll(fluct, shift=-dt, axis=1))) for dt in range(6)]
    c0 = max(1e-12, c_dt[0])
    c1 = max(1e-12, min(c0 * 0.95, c_dt[1]))
    m_lat = -math.log(c1 / c0)

    mw = {k: float(np.mean(v)) for k, v in w_acc.items()}
    chi_22 = -math.log(max(1e-12, mw["2x2"] * mw["1x1"]) / max(1e-12, mw["2x1"] * mw["1x2"]))
    sqrt_chi = math.sqrt(max(1e-9, chi_22))
    ratio = m_lat / sqrt_chi

    rng = np.random.default_rng(seed + 777)
    m_bs, chi_bs, ratio_bs = [], [], []
    for _ in range(B_BOOTSTRAP):
        idx = rng.integers(0, MEAS_SWEEPS, size=MEAS_SWEEPS)
        f = fluct[idx] - fluct[idx].mean()
        c0b = max(1e-12, float(np.mean(f * f)))
        c1b = max(1e-12, min(c0b * 0.95, float(np.mean(f * np.roll(f, shift=-1, axis=1)))))
        mb = -math.log(c1b / c0b)
        ww = {k: float(np.mean(np.array(v)[idx])) for k, v in w_acc.items()}
        chib = -math.log(max(1e-12, ww["2x2"] * ww["1x1"]) / max(1e-12, ww["2x1"] * ww["1x2"]))
        m_bs.append(mb)
        chi_bs.append(chib)
        ratio_bs.append(mb / math.sqrt(max(1e-9, chib)))

    return {
        "L": L,
        "seed": seed,
        "beta": BETA,
        "therm_sweeps": THERM_SWEEPS,
        "meas_sweeps": MEAS_SWEEPS,
        "wall_s": round(wall, 2),
        "C": [round(x, 8) for x in c_dt],
        "W": {k: round(v, 5) for k, v in mw.items()},
        "m_lat": round(m_lat, 4),
        "m_lat_err": round(float(np.std(m_bs)), 4),
        "chi_2x2": round(chi_22, 4),
        "chi_2x2_err": round(float(np.std(chi_bs)), 4),
        "ratio": round(ratio, 3),
        "ratio_err": round(float(np.std(ratio_bs)), 3),
    }


def main() -> None:
    print("=" * 92)
    print("TARGET E [CONTROL]: Cubic-3D SU(2) Reference for m_0++/sqrt(sigma)")
    print(f"beta = {BETA}, {THERM_SWEEPS} therm + {MEAS_SWEEPS} meas, APE {APE_ALPHA} x {APE_STEPS}, "
          f"bootstrap B = {B_BOOTSTRAP}")
    print("=" * 92)
    rows: List[Dict[str, Any]] = []
    for L in LATTICES:
        res = run_one_lattice(L, seed=3000 + L)
        rows.append(res)
        print(
            f"  L={L:<3} m = {res['m_lat']:.4f} +- {res['m_lat_err']:.4f}   "
            f"chi(2,2) = {res['chi_2x2']:.4f} +- {res['chi_2x2_err']:.4f}   "
            f"ratio = {res['ratio']:.3f} +- {res['ratio_err']:.3f}   [{res['wall_s']}s]"
        )
        print(f"        C(dt): " + "  ".join(f"C({d}) = {c:.3e}" for d, c in enumerate(res["C"])))

    # ---- Comparison against Target D (BCC) ----------------------------------
    l20 = rows[-1]
    l8 = rows[0]
    delta, verdict = None, None
    td_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glueball_scaling.json")
    if os.path.exists(td_path):
        with open(td_path) as fh:
            td = json.load(fh)
        td20 = next(r for r in td["rows"] if r["L"] == 20)
        delta = l20["ratio"] - td20["ratio"]
        comb_err = math.hypot(l20["ratio_err"], td20["ratio_err"])
        sigma = abs(delta) / comb_err if comb_err > 0 else float("inf")
        verdict = (
            "(i) LATTICE-UNIVERSAL (3D SU(2) property; reference must be the 3D continuum ratio)"
            if sigma <= 2.0
            else "(ii) BCC-SPECIFIC (diagonal geometry shifts the ratio; theory must account for it)"
        )
        print("-" * 92)
        print(f"  Target D (BCC)  L=20: ratio = {td20['ratio']:.3f} +- {td20['ratio_err']:.3f}")
        print(f"  Target E (cubic) L=20: ratio = {l20['ratio']:.3f} +- {l20['ratio_err']:.3f}")
        print(f"  delta = {delta:+.3f}  (combined err {comb_err:.3f}, {sigma:.2f} sigma)")
        print(f"  Preregistered verdict: {verdict}")
    else:
        print("-" * 92)
        print("  (glueball_scaling.json not found; Target D comparison deferred)")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cubic_control.json")
    with open(out, "w") as fh:
        json.dump({"protocol": "Target E, PREREGISTRATION.md item 7", "beta": BETA,
                   "rows": rows, "delta_vs_BCC_L20": delta, "verdict": verdict}, fh, indent=2)
    print(f"  Artifact: {out}")


if __name__ == "__main__":
    main()
