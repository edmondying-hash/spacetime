"""Target I [D1 Anchor A measurement]: BCC long ensemble — emergent gauge
tension & the 3D continuum reference value of m_0++/sqrt(sigma).

PREREGISTRATION.md item 10 (locked before execution):
  * Target F kernel, operator, and estimators inherited VERBATIM
    (imports bcc_glueball_scaling.run_one_lattice; the parallel-kernel
    equivalence validation of Target F carries over).
  * New protocol constants only: L = {24, 32, 40}, 2000 therm + 5000 meas,
    seed 4000 + L, bootstrap B = 2000. beta / APE / operator unchanged.
  * D1 anchor: sqrt(sigma) = 440 MeV (PDG data input) fixes the lattice unit
    u(L) = 440/sqrt(chi(L)) MeV; m_0++(MeV) = m_lat(L) * u(L). The NUMERICAL
    kappa (MeV/tick) is NOT claimed until the tick<->link coarse-graining
    scale (THEORY.md F2) is resolved — this target's F2-independent
    deliverable is sqrt(sigma) in lattice units plus finite-size stability.

Pass criteria (preregistered):
  (i)   ratio m/sqrt(sigma) within 2x combined bootstrap error of the
        Target F L=20 value (5.588 +- 0.249) at every L;
  (ii)  sqrt(chi(2,2)) stable across L within 2x combined errors;
  (iii) exploratory slope-fit mass within 2 sigma_m of the ratio estimator.

Heavy run: executed on the ED box (32-core Ryzen 7 WSL), NOT in the local CI
script suite. The committed artifact bcc/long_ensemble_bcc.json is verified
by CI assertion 16.
"""

import json
import math
import os
import sys
import time
from typing import Any, Dict


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcc_glueball_scaling as fg  # noqa: E402  (validated kernel, verbatim)

# ---- Preregistered protocol constants (Target I, locked) -------------------
LATTICES = [24, 32, 40]
THERM_SWEEPS = 2000
MEAS_SWEEPS = 5000
SEED_OFFSET = 4000
SQRT_SIGMA_PDG_MEV = 440.0     # PDG data input (D6 convention), declared
F2_CAVEAT = (
    "Numerical kappa (MeV/tick) is NOT fixed by this target: it requires the "
    "tick<->link coarse-graining scale (THEORY.md F2). Deliverable here is "
    "sqrt(sigma) in lattice units at L = 24/32/40 and its finite-size stability."
)


def main() -> None:
    t_start = time.time()
    print("=" * 78)
    print("TARGET I [D1 ANCHOR A MEASUREMENT]: BCC long ensemble, L = 24/32/40")
    print(f"SU(2) BCC MC beta = {fg.BETA} (Target F, verbatim kernel), "
          f"{THERM_SWEEPS} therm + {MEAS_SWEEPS} meas, seed = {SEED_OFFSET}+L, "
          f"APE {fg.APE_ALPHA} x {fg.APE_STEPS}, bootstrap B = {fg.B_BOOTSTRAP}")
    print(f"D1 anchor input: sqrt(sigma) = {SQRT_SIGMA_PDG_MEV} MeV (PDG data)")
    print("=" * 78)

    # The inherited run_one_lattice resolves sweep counts from the module
    # globals at call time; the preregistered extension is applied here ONLY.
    fg.THERM_SWEEPS = THERM_SWEEPS
    fg.MEAS_SWEEPS = MEAS_SWEEPS

    rows = []
    for L in LATTICES:
        seed = SEED_OFFSET + L
        print(f"\n--- L = {L} (seed {seed}) ---")
        res = fg.run_one_lattice(L, seed)
        rows.append(res)
        print(f"  m = {res['m_lat']:.4f} +- {res['m_lat_err']:.4f}  "
              f"sqrt(chi) = {res['sqrt_chi']:.4f} +- {res['chi_2x2_err']:.4f}")
        print(f"  ratio = {res['ratio']:.3f} +- {res['ratio_err']:.3f}   "
              f"wall = {res['wall_s']} s")

    # ---- D1 anchor block (F2-independent deliverable) ----
    d1 = {"sqrt_sigma_pdg_mev": SQRT_SIGMA_PDG_MEV, "by_L": {}}
    for r in rows:
        u = SQRT_SIGMA_PDG_MEV / max(1e-9, r["sqrt_chi"])
        d1["by_L"][str(r["L"])] = {
            "lattice_unit_mev": round(u, 3),
            "m0pp_mev": round(r["m_lat"] * u, 1),
            "m0pp_mev_err": round(r["m_lat_err"] * u, 1),
        }
    d1["f2_caveat"] = F2_CAVEAT

    # ---- Preregistered pass criteria ----
    f_art = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "glueball_scaling.json")
    f20 = next((r for r in json.load(open(f_art))["rows"] if r["L"] == 20), None)

    # (i) ratio stability vs Target F L=20
    combined = [
        (r["L"], abs(r["ratio"] - f20["ratio"]) /
         max(1e-9, 2.0 * math.sqrt(r["ratio_err"] ** 2 + f20["ratio_err"] ** 2)))
        for r in rows
    ]
    pass_i = f20 is not None and all(d <= 1.0 for _, d in combined)

    # (ii) tension stability (pairwise, 2x combined errors)
    pass_j = True
    for a in range(len(rows)):
        for b in range(a + 1, len(rows)):
            ra, rb = rows[a], rows[b]
            denom = 2.0 * math.sqrt(ra["chi_2x2_err"] ** 2 + rb["chi_2x2_err"] ** 2)
            if abs(ra["sqrt_chi"] - rb["sqrt_chi"]) / max(1e-9, denom) > 1.0:
                pass_j = False

    # (iii) estimator sanity
    pass_k = all(
        math.isfinite(r["m_fit_exploratory"]) and
        abs(r["m_fit_exploratory"] - r["m_lat"]) <= 2.0 * r["m_lat_err"]
        for r in rows
    )

    out = {
        "target": "I",
        "script": "bcc/bcc_long_ensemble_bcc.py",
        "protocol": {
            "kernel": "Target F verbatim (bcc_glueball_scaling.run_one_lattice)",
            "beta": fg.BETA,
            "therm_sweeps": THERM_SWEEPS,
            "meas_sweeps": MEAS_SWEEPS,
            "ape": f"alpha={fg.APE_ALPHA} x {fg.APE_STEPS} steps",
            "seed_offset": SEED_OFFSET,
            "bootstrap": fg.B_BOOTSTRAP,
        },
        "rows": rows,
        "d1_anchor": d1,
        "pass_i_ratio_stability": pass_i,
        "pass_i_detail": {f"L{L}": round(d, 3) for L, d in combined},
        "pass_ii_tension_stability": pass_j,
        "pass_iii_estimator_sanity": pass_k,
        "all_pass": bool(pass_i and pass_j and pass_k),
        "total_wall_s": round(time.time() - t_start, 1),
    }
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "long_ensemble_bcc.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2)

    print("\n" + "=" * 78)
    print("TARGET I SUMMARY")
    print(f"  D1 anchor: lattice unit u(L=24) = "
          f"{d1['by_L'][str(rows[0]['L'])]['lattice_unit_mev']:.1f} MeV "
          f"(L={rows[0]['L']}); m_0++ = "
          + ", ".join(f"{d1['by_L'][str(r['L'])]['m0pp_mev']:.0f} MeV" for r in rows))
    print(f"  (i) ratio stability vs F(L=20={f20['ratio'] if f20 else 'n/a'}): "
          f"{'PASS' if pass_i else 'FAIL'}  {out['pass_i_detail']}")
    print(f"  (ii) tension stability:      {'PASS' if pass_j else 'FAIL'}")
    print(f"  (iii) estimator sanity:      {'PASS' if pass_k else 'FAIL'}")
    print(f"  3D continuum reference (L=40): {rows[-1]['ratio']:.3f} +- {rows[-1]['ratio_err']:.3f}")
    print(f"  artifact: {dst}  (total wall {out['total_wall_s']} s)")
    print("=" * 78)


if __name__ == "__main__":
    main()
