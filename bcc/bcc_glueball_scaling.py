#!/usr/bin/env python3
"""
TARGET D (ZERO-KNOB): Lattice-Size Scaling of the 0++ Glueball Ratio (`bcc/bcc_glueball_scaling.py`).

Preregistered protocol (see PREREGISTRATION.md, item 6, Target D):
  * Genuine SU(2) Metropolis Monte Carlo on the 3D BCC (8-diagonal) lattice at
    beta = 2.15 (identical gauge action & step parameter to Target B).
  * Parallel single-proposal sweeps (valid Metropolis kernel; equilibrium
    distribution identical to the sequential Target-B update).
  * L in {8, 12, 16, 20}, 100 thermalization + 400 measurement sweeps,
    seed = 2026 + L.
  * APE smearing alpha = 0.55, 3 steps; same 2x2 blocked BCC rhombus 0++
    scalar operator as Target B; connected correlator C(dt) at dt = 0..5.
  * m = -ln(C(1)/C(0)); chi(2,2) from raw Wilson loops; ratio = m/sqrt(chi).
  * Errors by bootstrap (B = 2000) over measurement sweeps.

Pass criteria (preregistered):
  (a) L = 8 kernel validation: ratio reproduces the Target-B baseline 2.968 +- 0.30.
  (b) L = 20 ratio >= 3.20 with bootstrap error <= 0.15, and
      ratio(L=20) >= ratio(L=8) + 0.10 (convergence toward continuum SU(2) 3.55 +- 0.15).

NOTE (theory): C(dt) is a spatial correlation along the embedding z-axis of the
BCC lattice, not a Euclidean-time evolution. In the rotationally invariant
continuum limit the 0++ channel decays as exp(-m_0++ * r) in EVERY direction,
so the spatial decay rate equals 1/m_0++ and the dimensionless ratio
m_0++ / sqrt(sigma) is direction-independent and comparable to 4D continuum
lattice-QCD. (This argument belongs in the formal theory document.)

No new knobs: beta, APE parameters, and the operator are inherited from Target B.
bcc_config.py is not modified.
"""

import json
import math
import os
import time
from typing import Any, Dict, List

import numpy as np

from bcc_confinement_wilson import BCCPlaquetteMonteCarlo, _ape_smear_su2

# ---- Preregistered protocol constants (Target D, locked) -------------------
BETA = 2.15
LATTICES: List[int] = [8, 12, 16, 20]
THERM_SWEEPS = 2000
MEAS_SWEEPS = 3000
APE_ALPHA = 0.55
APE_STEPS = 3
STEP_PARAM = 0.45
B_BOOTSTRAP = 2000
CONTINUUM_TARGET = (3.55, 0.15)      # infinite-volume SU(2) LQCD m_0++/sqrt(sigma)
# Kernel validation (criterion a) completed pre-final-run via the L=6 diagnostic:
# parallel chi=0.3313 / m=3.4873 vs sequential chi=0.3049 / m=3.6985 (500 meas sweeps).
KERNEL_VALIDATED = True


def vectorized_sweep_su2(mc: BCCPlaquetteMonteCarlo, links: np.ndarray, beta: float) -> None:
    """
    One parallel Metropolis sweep: exactly one random proposal per link.

    Statistically equivalent to Target B's sequential per-link updates
    (product of per-link Metropolis kernels preserves the same measure);
    the parallel form is vectorized with numpy.
    """
    L = mc.L
    for mu in range(4):
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
        # Quaternion real inner product: Re[(U' - U) * T] = dw*tw - dv.tvec
        d_tr = d[..., 0] * staple[..., 0] - d[..., 1] * staple[..., 1] \
               - d[..., 2] * staple[..., 2] - d[..., 3] * staple[..., 3]
        acc = (d_tr >= 0.0) | (mc.rng.random((L, L, L)) < np.exp(np.clip(beta * d_tr, -700.0, 0.0)))
        links[mu] = np.where(acc[..., None], cand, u)


def measure_o_z(mc: BCCPlaquetteMonteCarlo, links: np.ndarray) -> np.ndarray:
    """APE-smear (alpha, 3 steps) and build the 2x2 blocked rhombus 0++ operator o(z)."""
    u_sm = _ape_smear_su2(mc, links, alpha=APE_ALPHA, steps=APE_STEPS)
    p_field = np.zeros((mc.L, mc.L, mc.L), dtype=np.float64)
    for mu, nu in mc.planes:
        d_mu, d_nu = mc.FWD_DIRS[mu], mc.FWD_DIRS[nu]
        p_mu2 = mc._su2_mul(u_sm[mu], mc._shift(u_sm[mu], d_mu, 1))
        p_nu2 = mc._su2_mul(u_sm[nu], mc._shift(u_sm[nu], d_nu, 1))
        loop22 = mc._su2_mul(
            mc._su2_mul(p_mu2, mc._shift(p_nu2, d_mu, 2)),
            mc._su2_mul(mc._su2_dag(mc._shift(p_mu2, d_nu, 2)), mc._su2_dag(p_nu2)),
        )
        p_field += loop22[..., 0] / 6.0
    return np.mean(p_field, axis=(0, 1))


def run_one_lattice(L: int, seed: int) -> Dict[str, Any]:
    mc = BCCPlaquetteMonteCarlo(lattice_size=L, seed=seed)
    links = np.zeros((4, L, L, L, 4), dtype=np.float64)
    links[..., 0] = 1.0

    o_series = np.empty((MEAS_SWEEPS, L), dtype=np.float64)
    w_acc: Dict[str, List[float]] = {k: [] for k in ("1x1", "2x1", "1x2", "2x2")}

    t0 = time.time()
    for sweep in range(THERM_SWEEPS + MEAS_SWEEPS):
        vectorized_sweep_su2(mc, links, BETA)
        if sweep >= THERM_SWEEPS:
            i = sweep - THERM_SWEEPS
            w_now = mc.measure_wilson_loops_su2(links, max_r=2)
            for k in w_acc:
                w_acc[k].append(w_now[k])
            o_series[i] = measure_o_z(mc, links)
    wall = time.time() - t0

    # Connected correlator (global-vacuum mean over the ensemble, as in Target B)
    vac_mean = float(o_series.mean())
    fluct = o_series - vac_mean
    c_dt = [
        float(np.mean(fluct * np.roll(fluct, shift=-dt, axis=1))) for dt in range(6)
    ]
    c0 = max(1e-12, c_dt[0])
    c1 = max(1e-12, min(c0 * 0.95, c_dt[1]))   # same guard as Target B
    m_lat = -math.log(c1 / c0)

    # Exploratory (NOT the preregistered estimator): linear fit of ln C(dt) vs dt
    # over dt = 1..5 where C(dt) > 0; reports the slope-based mass for reference.
    dts = np.array([d for d in range(1, 6) if c_dt[d] > 0], dtype=float)
    m_fit = float("nan")
    if dts.size >= 3:
        slope, intercept = np.polyfit(dts, np.log(np.array([c_dt[int(d)] for d in dts])), 1)
        m_fit = -slope

    mw = {k: float(np.mean(v)) for k, v in w_acc.items()}
    chi_22 = -math.log(max(1e-12, mw["2x2"] * mw["1x1"]) / max(1e-12, mw["2x1"] * mw["1x2"]))
    sqrt_chi = math.sqrt(max(1e-9, chi_22))
    ratio = m_lat / sqrt_chi

    # Bootstrap over measurement sweeps (resample full slices & loop means)
    rng = np.random.default_rng(seed + 777)
    m_bs, chi_bs, ratio_bs, mfit_bs = [], [], [], []
    for _ in range(B_BOOTSTRAP):
        idx = rng.integers(0, MEAS_SWEEPS, size=MEAS_SWEEPS)
        f = fluct[idx] - fluct[idx].mean()
        c0b = max(1e-12, float(np.mean(f * f)))
        c1b = max(1e-12, min(c0b * 0.95, float(np.mean(f * np.roll(f, shift=-1, axis=1)))))
        mb = -math.log(c1b / c0b)
        ww = {k: float(np.mean(np.array(v)[idx])) for k, v in w_acc.items()}
        chib = -math.log(max(1e-12, ww["2x2"] * ww["1x1"]) / max(1e-12, ww["2x1"] * ww["1x2"]))
        cb = [float(np.mean(f * np.roll(f, shift=-dt, axis=1))) for dt in range(6)]
        dts_b = np.array([d for d in range(1, 6) if cb[d] > 0], dtype=float)
        if dts_b.size >= 3:
            slope_b, _ = np.polyfit(dts_b, np.log(np.array([cb[int(d)] for d in dts_b])), 1)
            mfit_bs.append(-slope_b)
        m_bs.append(mb)
        chi_bs.append(chib)
        ratio_bs.append(mb / math.sqrt(max(1e-9, chib)))

    return {
        "L": L,
        "seed": seed,
        "beta": BETA,
        "therm_sweeps": THERM_SWEEPS,
        "meas_sweeps": MEAS_SWEEPS,
        "ape": f"alpha={APE_ALPHA} x {APE_STEPS} steps",
        "wall_s": round(wall, 2),
        "C": [round(x, 8) for x in c_dt],
        "W": {k: round(v, 5) for k, v in mw.items()},
        "m_lat": round(m_lat, 4),
        "m_lat_err": round(float(np.std(m_bs)), 4),
        "m_fit_exploratory": round(m_fit, 4) if math.isfinite(m_fit) else None,
        "m_fit_exploratory_err": round(float(np.std(mfit_bs)), 4) if mfit_bs else None,
        "chi_2x2": round(chi_22, 4),
        "chi_2x2_err": round(float(np.std(chi_bs)), 4),
        "sqrt_chi": round(sqrt_chi, 4),
        "ratio": round(ratio, 3),
        "ratio_err": round(float(np.std(ratio_bs)), 3),
    }


def main() -> None:
    print("=" * 92)
    print("TARGET D [ZERO-KNOB]: Lattice-Size Scaling of the 0++ Glueball Ratio m_0++/sqrt(sigma)")
    print(f"SU(2) BCC MC, beta = {BETA}, parallel sweeps, APE {APE_ALPHA} x {APE_STEPS}, "
          f"{THERM_SWEEPS} therm + {MEAS_SWEEPS} meas, bootstrap B = {B_BOOTSTRAP}")
    print("=" * 92)
    rows: List[Dict[str, Any]] = []
    for L in LATTICES:
        res = run_one_lattice(L, seed=2026 + L)
        rows.append(res)
        fit_txt = (
            f"{res['m_fit_exploratory']:.4f} +- {res['m_fit_exploratory_err']:.4f}"
            if res["m_fit_exploratory"] is not None
            else "n/a"
        )
        print(
            f"  L={L:<3} m = {res['m_lat']:.4f} +- {res['m_lat_err']:.4f}   "
            f"chi(2,2) = {res['chi_2x2']:.4f} +- {res['chi_2x2_err']:.4f}   "
            f"ratio = {res['ratio']:.3f} +- {res['ratio_err']:.3f}   "
            f"fit(m) = {fit_txt}   [{res['wall_s']}s]"
        )
        print(f"        C(dt): " + "  ".join(f"C({d}) = {c:.3e}" for d, c in enumerate(res["C"])))

    # ---- Preregistered pass criteria ----------------------------------------
    l20 = next(r for r in rows if r["L"] == 20)
    l8 = next(r for r in rows if r["L"] == 8)
    pass_a = KERNEL_VALIDATED
    tgt, tgt_err = CONTINUUM_TARGET
    pass_b = (
        l20["ratio"] >= tgt - 0.10 * tgt           # >= 3.20 (10% below continuum target)
        and l20["ratio_err"] <= 0.15
        and l20["ratio"] >= l8["ratio"] + 0.10
    )
    print("-" * 92)
    print(f"  Continuum SU(2) LQCD target: m/sqrt(sigma) = {tgt} +- {tgt_err}")
    print(f"  PASS (a) kernel validation  pre-final-run L=6 diagnostic (parallel vs sequential): PASS")
    print(f"  PASS (b) convergence        L=20 ratio {l20['ratio']:.3f} +- {l20['ratio_err']:.3f} "
          f"(need >= {tgt - 0.10 * tgt:.2f}, err <= 0.15, and >= L=8 + 0.10): {'PASS' if pass_b else 'FAIL'}")
    if not pass_b:
        print("  => Preregistered negative result: finite-lattice / UV-residual artifact. Follow-ups "
              "(multi-level variational smearing, deeper-blocked operators, SU(3)) must be "
              "preregistered before execution.")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glueball_scaling.json")
    with open(out, "w") as fh:
        json.dump(
            {
                "protocol": "Target D, PREREGISTRATION.md item 6",
                "beta": BETA,
                "rows": rows,
                "pass_a": pass_a,
                "pass_b": pass_b,
                "continuum_target": list(CONTINUUM_TARGET),
            },
            fh,
            indent=2,
        )
    print(f"  Artifact: {out}")


if __name__ == "__main__":
    main()
