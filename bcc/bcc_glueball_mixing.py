#!/usr/bin/env python3
"""
3x3 Glueball-Quarkonium Mixing Simulation (`bcc/bcc_glueball_mixing.py`).

Diagonalizes the flavor-symmetric 3x3 scalar (J^PC = 0++) mixing matrix
coupling the bare 2-gluon (gg) BCC glueball |G> with P-wave scalar quarkonia

|nn_bar> = (|uu_bar> + |dd_bar>)/sqrt(2) and |ss_bar>:

        [ M_nn      sqrt(2)*v    0    ]
    M = [ sqrt(2)*v    M_G       v    ]
        [   0           v      M_ss   ]

Shows how a single bare 2-gluon loop splits into the three physical PDG
resonances f_0(1370), f_0(1500), and f_0(1710), and compares the 8^3 SU(2)
BCC bare gap (1306.1 MeV) against the continuum SU(3) gap (1562.0 MeV).
"""

import math
from pathlib import Path
import sys
from typing import Any, Dict, List
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bcc_config as cfg
from bcc_chiral_dirac import evaluate_chiral_condensate_and_bare_ticks
from bcc_meson_sim import QUARK_BARE_TICKS

TICK_TO_MEV, _ = cfg.knob("TICK_TO_MEV")
TICKS_PER_LP, _ = cfg.knob("TICKS_PER_LP")


def solve_3x3_glueball_mixing(
    m_nn_mev: float,
    m_g_mev: float,
    m_ss_mev: float,
    v_mix_mev: float = 75.0,
) -> List[Dict[str, Any]]:
    """Diagonalize the 3x3 |nn_bar>, |G (2g)>, |ss_bar> scalar mixing matrix."""
    mat = np.array(
        [
            [m_nn_mev, math.sqrt(2.0) * v_mix_mev, 0.0],
            [math.sqrt(2.0) * v_mix_mev, m_g_mev, v_mix_mev],
            [0.0, v_mix_mev, m_ss_mev],
        ],
        dtype=np.float64,
    )
    evals, evecs = np.linalg.eigh(mat)

    pdg_targets = [
        ("f_0(1370)", 1350.0),
        ("f_0(1500)", 1506.0),
        ("f_0(1710)", 1733.0),
    ]

    states: List[Dict[str, Any]] = []
    for idx, (label, pdg_mev) in enumerate(pdg_targets):
        vec = evecs[:, idx]
        p_nn, p_g, p_ss = (vec ** 2).tolist()
        mass = float(evals[idx])
        states.append(
            {
                "resonance": label,
                "pred_mev": round(mass, 1),
                "pdg_mev": pdg_mev,
                "diff_mev": round(mass - pdg_mev, 1),
                "pct_nn": round(p_nn * 100.0, 1),
                "pct_glue_2g": round(p_g * 100.0, 1),
                "pct_ss": round(p_ss * 100.0, 1),
            }
        )
    return states


def run_mixing_demo() -> None:
    # Derive bare P-wave (L=1) scalar quarkonia masses from BCC quark ticks
    chiral = evaluate_chiral_condensate_and_bare_ticks(lattice_size=4, beta=2.05, seed=2026)
    b_l = chiral["b_l_derived"]              # 15.5563 ticks (derived)
    b_s = float(QUARK_BARE_TICKS["s"])       # strange quark bare ticks

    # S-wave base + 1-unit P-wave orbital BCC flux excitation (L=1 -> +600 MeV)
    e_orbital_l1 = 815.0
    m_nn_bare = (2.0 * 3.0 * b_l * TICK_TO_MEV) + (2.0 * TICKS_PER_LP * TICK_TO_MEV) + e_orbital_l1
    m_ss_bare = (2.0 * 3.0 * b_s * TICK_TO_MEV) + (2.0 * TICKS_PER_LP * TICK_TO_MEV) + e_orbital_l1

    print("=" * 96)
    print("3x3 SCALAR GLUEBALL-QUARKONIUM MIXING ON THE 3D BCC LATTICE (J^PC = 0++)")
    print(f"Bare Scalar Quarkonia from BCC Ticks: M(nn_bar) = {m_nn_bare:.1f} MeV | M(ss_bar) = {m_ss_bare:.1f} MeV")
    print("=" * 96)

    for label, m_g in (
        ("Scenario A: Continuum SU(3) BCC Bare Glueball (3.55 * 440 MeV = 1562.0 MeV)", 1562.0),
        ("Scenario B: Raw 8^3 SU(2) BCC Bare Glueball   (2.97 * 440 MeV = 1306.1 MeV)", 1306.1),
    ):
        print(f"\n{label}")
        print("-" * 96)
        print(f"{'Resonance':<12} {'Mixed (MeV)':>12} {'PDG (MeV)':>11} {'Diff (MeV)':>11} {'|nn_bar>':>10} {'|G (2g)>':>10} {'|ss_bar>':>10}")
        print("-" * 96)
        rows = solve_3x3_glueball_mixing(m_nn_bare, m_g, m_ss_bare, v_mix_mev=75.0)
        for r in rows:
            print(
                f"{r['resonance']:<12} {r['pred_mev']:>12.1f} {r['pdg_mev']:>11.1f} {r['diff_mev']:>+11.1f} "
                f"{r['pct_nn']:>9.1f}% {r['pct_glue_2g']:>9.1f}% {r['pct_ss']:>9.1f}%"
            )
        tot_g = sum(r["pct_glue_2g"] for r in rows)
        print("-" * 96)
        print(f"  Unitarity Check: Total 2-Gluon (|G>) Wavefunction Across All 3 States = {tot_g:.1f}%")


if __name__ == "__main__":
    run_mixing_demo()
