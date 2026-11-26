"""Target K [D3 — Baryon Tick-Structure Re-derivation].

PREREGISTRATION.md item 12 (locked before execution). Objective: a baryon
mass dictionary on the SAME single scale as the meson sector (one
kappa = 5.0 MeV/tick, no per-hadron retuning), built only from in-theory
ingredients.

Inputs (declared, shared with the meson sector — no new knobs):
  b_l = 15.5563 ticks (Target C chiral-gap derivation, zero bare-tick fit)
  b_s = 24.25 ticks (meson dictionary, declared)
  kappa = 5.0 (meson sector)
  BCC 8^3 graph, redraw probs {l: 0.72, s: 0.40} (meson-sim values)
  w_hop = TICKS_PER_LP * sqrt(3) = 27.0 ticks/hop (diagonal hop = sqrt(3) lP)
  seed 42, 3000 cycles, start (1,1,1)/(4,4,4)/(6,2,6), periodic boundary.

v1 (spin-as-routing-topology):
  M = kappa * [B + w_hop * L_J]
  L_J: J=3/2 -> 3-terminal exact Steiner tree (no diquark pairing);
       J=1/2 -> 2-terminal routing (spin-0 diquark of the two lightest
       quarks at their midpoint + third quark).

v2 (declared branch, M/M/1 congestion time — the D2 queue-theory term):
  M = kappa * [B + w_hop * (L_J + sum_f (1-p_f)/p_f * L_J/3)]

Pass criteria: (i) Delta-N within 25% of 293 MeV; (ii) all 8 baryons within
5% (nucleon within 2%) with one kappa. Failures are declared theory
failures with the shortfall decomposition recorded.
"""

import itertools
import json
import math
import os
import random
import sys
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bcc_unified_engine import build_periodic_bcc_graph  # noqa: E402

# ---- Preregistered protocol constants (Target K, locked) -------------------
SIZE = 8
B_L = 15.5563          # Target C derived (zero bare-tick fit)
B_S = 24.25            # meson dictionary (declared)
KAPPA = 5.0            # meson sector single scale
W_HOP = 27.0           # TICKS_PER_LP * sqrt(3)
REDRAW = {"l": 0.72, "s": 0.40}
SEED = 42
CYCLES = 3000
START3 = [(1, 1, 1), (4, 4, 4), (6, 2, 6)]
DIRS = tuple(itertools.product((-1, 1), repeat=3))

BARYONS: List[Tuple[str, List[str], str, float]] = [
    ("N",         ["l", "l", "l"], "1/2", 938.9),
    ("Delta",     ["l", "l", "l"], "3/2", 1232.0),
    ("Lambda",    ["l", "l", "s"], "1/2", 1116.0),
    ("Sigma",     ["l", "l", "s"], "1/2", 1189.0),
    ("Xi",        ["l", "s", "s"], "1/2", 1315.0),
    ("SigmaStar", ["l", "l", "s"], "3/2", 1385.0),
    ("XiStar",    ["l", "s", "s"], "3/2", 1530.0),
    ("Omega",     ["s", "s", "s"], "3/2", 1672.0),
]


def _bcc_dist(p: Tuple[int, int, int], q: Tuple[int, int, int]) -> int:
    return max(min(abs(a - b), SIZE - abs(a - b)) for a, b in zip(p, q))


def _steiner3(sites, p1, p2, p3) -> int:
    return min(_bcc_dist(p1, j) + _bcc_dist(p2, j) + _bcc_dist(p3, j)
               for j in sites)


def _parity_fix(p: List[int]) -> Tuple[int, int, int]:
    p = [x % SIZE for x in p]
    if not (p[0] % 2 == p[1] % 2 == p[2] % 2):
        p[0] = (p[0] + 1) % SIZE
    return tuple(p)


def measure_L(flavors: List[str], J: str, sites) -> float:
    """Mean routing tree length under the spin routing rule (prereg v1)."""
    r = random.Random(SEED)
    a, b, c = START3
    if J == "3/2":
        pos = [list(a), list(b), list(c)]
        fs = flavors
    else:
        diq = _parity_fix([(a[0] + b[0]) // 2, (a[1] + b[1]) // 2,
                           (a[2] + b[2]) // 2])
        pos = [list(diq), list(c)]
        fs = [flavors[0], flavors[2]]     # two lightest paired, third free
    tot = 0.0
    for _ in range(CYCLES):
        for i, f in enumerate(fs):
            if r.random() < REDRAW[f]:
                d = DIRS[r.randrange(8)]
                pos[i] = [(pos[i][k] + d[k]) % SIZE for k in range(3)]
        if len(pos) == 3:
            tot += _steiner3(sites, tuple(pos[0]), tuple(pos[1]), tuple(pos[2]))
        else:
            tot += _bcc_dist(tuple(pos[0]), tuple(pos[1]))
    return tot / CYCLES


def main() -> None:
    print("=" * 78)
    print("TARGET K [D3]: Baryon Tick-Structure Re-derivation (v1 + declared v2)")
    print(f"kappa = {KAPPA} (meson sector), b_l = {B_L} (Target C), b_s = {B_S}, "
          f"w_hop = {W_HOP}, seed = {SEED}, cycles = {CYCLES}")
    print("=" * 78)

    sites, _ = build_periodic_bcc_graph(SIZE)
    rows = []
    for name, fl, J, pdg in BARYONS:
        L = measure_L(fl, J, sites)
        B = sum(B_S if f == "s" else B_L for f in fl)
        cong = sum((1.0 - REDRAW[f]) / REDRAW[f] for f in fl) * (L / 3.0)
        m_v1 = KAPPA * (B + W_HOP * L)
        m_v2 = KAPPA * (B + W_HOP * (L + cong))
        rows.append({
            "name": name, "flavor": "".join(fl), "J": J,
            "L_J": round(L, 4), "B_ticks": round(B, 2),
            "congestion_ticks": round(W_HOP * cong, 2),
            "v1_mev": round(m_v1, 1), "v2_mev": round(m_v2, 1),
            "pdg_mev": pdg,
            "v1_diff_pct": round(100.0 * (m_v1 - pdg) / pdg, 2),
            "v2_diff_pct": round(100.0 * (m_v2 - pdg) / pdg, 2),
        })
        print(f"  {name:12s} {J:3s} L={L:6.3f}  v1={m_v1:8.1f} ({100*(m_v1-pdg)/pdg:+7.2f}%)  "
              f"v2={m_v2:8.1f} ({100*(m_v2-pdg)/pdg:+7.2f}%)  PDG={pdg:8.1f}")

    by = {r["name"]: r for r in rows}
    dn_v1 = by["Delta"]["v1_mev"] - by["N"]["v1_mev"]
    dn_v2 = by["Delta"]["v2_mev"] - by["N"]["v2_mev"]
    dn_pdg = 1232.0 - 938.9

    # ---- Preregistered pass criteria ----
    pass_i = abs(dn_v1 - dn_pdg) / dn_pdg <= 0.25          # v1 spin mechanism
    pass_ii_v1 = all(abs(r["v1_diff_pct"]) <= 5.0 for r in rows) \
        and abs(by["N"]["v1_diff_pct"]) <= 2.0
    pass_ii_v2 = all(abs(r["v2_diff_pct"]) <= 5.0 for r in rows) \
        and abs(by["N"]["v2_diff_pct"]) <= 2.0

    out = {
        "target": "K",
        "script": "bcc/bcc_baryon_rederivation.py",
        "protocol": {
            "kappa": KAPPA, "b_l": B_L, "b_s": B_S, "w_hop": W_HOP,
            "redraw": REDRAW, "seed": SEED, "cycles": CYCLES, "size": SIZE,
            "v1": "M = kappa*(B + w_hop*L_J); L_J: 3t Steiner (J=3/2) / 2t diquark (J=1/2)",
            "v2": "M = kappa*(B + w_hop*(L_J + sum_f (1-p_f)/p_f * L_J/3)) [M/M/1 congestion time]",
        },
        "rows": rows,
        "delta_minus_N": {
            "v1_mev": round(dn_v1, 1), "v2_mev": round(dn_v2, 1),
            "pdg_mev": dn_pdg,
        },
        "pass_i_spin_mechanism_v1": bool(pass_i),
        "pass_ii_full_spectrum_v1": bool(pass_ii_v1),
        "pass_ii_full_spectrum_v2": bool(pass_ii_v2),
        "shortfall_decomposition": {
            "note": ("v1 under-scales all baryons (base deficit) with the deficit "
                     "growing with strangeness; v2 (congestion time) lifts the "
                     "strange baryons by the D2 queue-theory per-s increment. "
                     "Any residual base deficit (light J=1/2 baryons) is the "
                     "sustained-confinement-workload term — declared open under "
                     "F1 dynamics / the D1 anchor, NOT fixed ad hoc."),
        },
    }
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "baryon_rederivation.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2)

    print("=" * 78)
    print(f"  Delta-N: v1 = {dn_v1:.1f} MeV (PDG {dn_pdg:.1f}, {100*(dn_v1-dn_pdg)/dn_pdg:+.1f}%)  "
          f"v2 = {dn_v2:.1f} MeV ({100*(dn_v2-dn_pdg)/dn_pdg:+.1f}%)")
    print(f"  (i) spin mechanism (v1, 25% bound):    {'PASS' if pass_i else 'FAIL'}")
    print(f"  (ii) full spectrum v1 (5%/2% bounds):  {'PASS' if pass_ii_v1 else 'FAIL'}  "
          f"(declared theory failure if FAIL)")
    print(f"  (ii) full spectrum v2 (5%/2% bounds):  {'PASS' if pass_ii_v2 else 'FAIL'}  "
          f"(declared theory failure if FAIL)")
    print(f"  artifact: {dst}")
    print("=" * 78)


if __name__ == "__main__":
    main()
