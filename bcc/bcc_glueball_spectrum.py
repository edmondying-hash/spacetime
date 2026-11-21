#!/usr/bin/env python3
"""
Multi-Channel 3D BCC SU(3) Glueball Spectrum (`bcc/bcc_glueball_spectrum.py`).

Compares three distinct color-singlet glueball channels on the exact same 3D BCC
SU(3) gauge ensemble (8^3 lattice, beta = 5.65, 2-step APE smearing):
  1. 0++ Scalar  (2g, C = +1): Symmetric sum of 4-link BCC rhombus Re Tr(P)
  2. 2++ Tensor  (2g, C = +1): Quadrupole difference Re Tr(P_01 - P_23)
  3. 1+- Odderon (3g, C = -1): 6-link non-planar 3D BCC chiral loop Im Tr(U_1 U_2 U_3 U_1^+ U_2^+ U_3^+)
     (Requires true 3-color SU(3); identically zero in SU(2)!)
"""

import math
from pathlib import Path
import sys
from typing import Dict, List
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bcc_su3_glueball_scaling import (
    FWD_DIRS,
    PLANES,
    SQRT_SIGMA_PHYS_MEV,
    _ape_smear_su3,
    _dag,
    _measure_wilson_su3,
    _random_su3_updates,
    _shift,
    _staple_sum_su3,
)


def _extract_effective_mass(series: List[np.ndarray]) -> float:
    """Extract spatial z-slice effective mass a*m = -ln(C(1)/C(0)) per configuration."""
    arr = np.array(series)
    fluct = arr - np.mean(arr, axis=1, keepdims=True)
    c0 = max(1e-12, float(np.mean(fluct * fluct)))
    c1 = max(1e-12, min(c0 * 0.98, float(np.mean(fluct * np.roll(fluct, shift=-1, axis=1)))))
    return -math.log(c1 / c0)


def measure_multi_channel_glueballs(
    lattice_size: int = 8,
    beta: float = 5.65,
    therm_sweeps: int = 25,
    meas_sweeps: int = 75,
    seed: int = 2026,
) -> Dict[str, Dict[str, float]]:
    """Measure 0++ (2g), 2++ (2g), and 1+- (3g) glueball masses on 3D BCC SU(3)."""
    rng = np.random.default_rng(seed)
    L = lattice_size
    links = np.zeros((4, L, L, L, 3, 3), dtype=np.complex128)
    links[..., 0, 0] = 1.0
    links[..., 1, 1] = 1.0
    links[..., 2, 2] = 1.0

    ax = np.arange(L)
    cb = (ax[:, None, None] + ax[None, :, None] + np.zeros((1, 1, L), dtype=int)) % 2
    parity_masks = [(cb == p) for p in (0, 1)]

    s_0pp: List[np.ndarray] = []
    s_2pp: List[np.ndarray] = []
    s_1pm: List[np.ndarray] = []
    acc_w = {"1x1": [], "2x1": [], "1x2": [], "2x2": []}

    # 4 non-planar 3-axis chiral triples on the 8-diagonal BCC crystal
    triples = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]

    for sweep in range(therm_sweeps + meas_sweeps * 3):
        for mu in range(4):
            for mask in parity_masks:
                staple = _staple_sum_su3(links, mu)
                u_old = links[mu][mask]
                st_sub = staple[mask]
                rand_step = _random_su3_updates(rng, (len(u_old),), eps=0.28)
                u_new = rand_step @ u_old

                d_tr = np.real(np.einsum("nij,nij->n", u_new - u_old, np.conjugate(st_sub)))
                prob = np.exp(np.minimum(0.0, (beta / 3.0) * d_tr))
                accept = (d_tr >= 0.0) | (rng.random(len(u_old)) < prob)
                u_old[accept] = u_new[accept]
                links[mu][mask] = u_old

        if sweep >= therm_sweeps and ((sweep - therm_sweeps) % 3 == 0):
            w_now = _measure_wilson_su3(links)
            for k in acc_w:
                acc_w[k].append(w_now[k])

            u_sm = _ape_smear_su3(links, alpha=0.55, steps=2)

            # Compute all 6 elementary 4-link BCC rhombus traces
            plaq_re = []
            for mu, nu in PLANES:
                d_mu, d_nu = FWD_DIRS[mu], FWD_DIRS[nu]
                loop11 = u_sm[mu] @ _shift(u_sm[nu], d_mu, 1) @ _dag(_shift(u_sm[mu], d_nu, 1)) @ _dag(u_sm[nu])
                plaq_re.append(np.real(np.trace(loop11, axis1=-2, axis2=-1)) / 3.0)

            # 1. 0++ Scalar (2g): symmetric average of all 6 BCC rhombus planes
            op_0pp = sum(plaq_re) / 6.0

            # 2. 2++ Tensor (2g): quadrupole anisotropy between orthogonal BCC rhombus pairs
            p0, p1, p2, p3, p4, p5 = plaq_re
            op_2pp = 0.5 * ((p0 - p5) + (p1 - p4))

            # 3. 1+- Odderon (3g, C = -1): 6-link non-planar 3D BCC chiral hexagon Im Tr(...)
            op_1pm = np.zeros((L, L, L), dtype=np.float64)
            for mu, nu, rho in triples:
                d_mu, d_nu, d_rho = FWD_DIRS[mu], FWD_DIRS[nu], FWD_DIRS[rho]
                u1 = u_sm[mu]
                u2 = _shift(u_sm[nu], d_mu, 1)
                u3 = _shift(_shift(u_sm[rho], d_mu, 1), d_nu, 1)
                u4 = _dag(_shift(_shift(u_sm[mu], d_nu, 1), d_rho, 1))
                u5 = _dag(_shift(u_sm[nu], d_rho, 1))
                u6 = _dag(u_sm[rho])
                hex_loop = u1 @ u2 @ u3 @ u4 @ u5 @ u6
                op_1pm += np.imag(np.trace(hex_loop, axis1=-2, axis2=-1)) / (3.0 * len(triples))

            s_0pp.append(np.mean(op_0pp, axis=(0, 1)))
            s_2pp.append(np.mean(op_2pp, axis=(0, 1)))
            s_1pm.append(np.mean(op_1pm, axis=(0, 1)))

    mw = {k: float(np.mean(v)) for k, v in acc_w.items()}
    chi_22 = -math.log(max(1e-12, mw["2x2"] * mw["1x1"]) / max(1e-12, mw["2x1"] * mw["1x2"]))
    sqrt_sigma = math.sqrt(max(1e-9, chi_22))

    m0 = _extract_effective_mass(s_0pp)
    m2 = _extract_effective_mass(s_2pp)
    m3 = _extract_effective_mass(s_1pm)

    out: Dict[str, Dict[str, float]] = {}
    for label, m_lat, n_gluons in (
        ("0++ Scalar (2g, C=+1)", m0, 2),
        ("2++ Tensor (2g, C=+1)", m2, 2),
        ("1+- Odderon (3g, C=-1)", m3, 3),
    ):
        ratio_sig = m_lat / sqrt_sigma
        out[label] = {
            "gluons": n_gluons,
            "a_m": round(m_lat, 4),
            "m_over_sqrt_sigma": round(ratio_sig, 3),
            "mass_mev": round(ratio_sig * SQRT_SIGMA_PHYS_MEV, 1),
            "ratio_to_0pp": round(m_lat / max(1e-9, m0), 2),
        }
    return out


def run_spectrum_comparison() -> None:
    print("=" * 94)
    print("3D BCC SU(3) MULTI-CHANNEL GLUEBALL SPECTRUM: 2-Gluon (gg) vs. 3-Gluon (ggg)")
    print("8^3 BCC Lattice | beta = 5.65 | 2-Step APE Smearing | sqrt(sigma) = 440 MeV")
    print("=" * 94)
    print(f"{'Channel (J^PC)':<25} {'Gluons':>6} {'a*m_lat':>9} {'m/√σ':>8} {'Mass (MeV)':>12} {'M / M(0++)':>12} {'QCD Ratio':>11}")
    print("-" * 94)
    qcd_ref = {
        "0++ Scalar (2g, C=+1)": "1.00x (ref)",
        "2++ Tensor (2g, C=+1)": "~1.40x",
        "1+- Odderon (3g, C=-1)": "~1.75x",
    }
    res = measure_multi_channel_glueballs(lattice_size=8, beta=5.65, therm_sweeps=25, meas_sweeps=75, seed=2026)
    for ch, d in res.items():
        print(
            f"{ch:<25} {d['gluons']:>5}g {d['a_m']:>9.4f} {d['m_over_sqrt_sigma']:>8.3f} "
            f"{d['mass_mev']:>10.1f} MeV {d['ratio_to_0pp']:>10.2f}x {qcd_ref[ch]:>11}"
        )
    print("-" * 94)
    print("  1-Gluon (1g): Forbidden (colored octet; cannot form a closed trace on BCC)")
    print("  2-Gluon (2g): Lightest closed 4-link rhombus (0++ scalar -> 2++ tensor quadrupole)")
    print("  3-Gluon (3g): Non-planar 6-link chiral BCC loop Im Tr(...) (requires true SU(3))")


if __name__ == "__main__":
    run_spectrum_comparison()
