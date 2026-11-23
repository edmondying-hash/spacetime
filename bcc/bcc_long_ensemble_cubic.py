"""Target J [Target G refinement]: cubic-3D long ensemble — shrink the
bootstrap errors of the cubic control so the BCC-vs-cubic delta at large L
is statistically meaningful.

PREREGISTRATION.md item 11 (locked before execution):
  * Target G cubic kernel, operator, and estimators inherited VERBATIM
    (imports bcc_cubic_control.run_one_lattice; APE staple /4, the 3D
    analogue of the BCC code's /6).
  * New protocol constants only: L = {24, 32, 40}, 2000 therm + 5000 meas,
    seed 3500 + L, bootstrap B = 2000. beta / APE / operator unchanged.

Pass criteria (preregistered):
  (i)   cubic ratio within 2x combined bootstrap error of the Target I BCC
        ratio at the same L (at every L) -> Target G verdict (i)
        LATTICE-UNIVERSAL confirmed at large L;
  (ii)  cubic bootstrap error at L = 40 <= 0.95 (Target G L = 20 error).

Execution order: runs AFTER Target I (criterion (i) needs the Target I
artifact). Heavy run on the ED box; NOT in the local CI script suite.
Committed artifact bcc/long_ensemble_cubic.json verified by CI assertion 16.
"""

import json
import math
import os
import sys
import time
from typing import Any, Dict


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcc_cubic_control as cg  # noqa: E402  (validated cubic kernel, verbatim)

# ---- Preregistered protocol constants (Target J, locked) -------------------
LATTICES = [24, 32, 40]
THERM_SWEEPS = 2000
MEAS_SWEEPS = 5000
SEED_OFFSET = 3500
G_L20_RATIO_ERR = 0.95        # Target G cubic L=20 bootstrap error (recorded)


def main() -> None:
    t_start = time.time()
    print("=" * 78)
    print("TARGET J [TARGET G REFINEMENT]: cubic-3D long ensemble, L = 24/32/40")
    print(f"SU(2) cubic MC beta = {cg.BETA} (Target G, verbatim kernel), "
          f"{THERM_SWEEPS} therm + {MEAS_SWEEPS} meas, seed = {SEED_OFFSET}+L, "
          f"APE {cg.APE_ALPHA} x {cg.APE_STEPS}, bootstrap B = {cg.B_BOOTSTRAP}")
    print("=" * 78)

    i_art = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "long_ensemble_bcc.json")
    if not os.path.exists(i_art):
        raise SystemExit("Target I artifact missing — run bcc_long_ensemble_bcc.py first.")
    i_by_l = {r["L"]: r for r in json.load(open(i_art))["rows"]}

    cg.THERM_SWEEPS = THERM_SWEEPS
    cg.MEAS_SWEEPS = MEAS_SWEEPS

    rows = []
    for L in LATTICES:
        seed = SEED_OFFSET + L
        print(f"\n--- L = {L} (seed {seed}) ---")
        res = cg.run_one_lattice(L, seed)
        rows.append(res)
        print(f"  m = {res['m_lat']:.4f} +- {res['m_lat_err']:.4f}   "
              f"ratio = {res['ratio']:.3f} +- {res['ratio_err']:.3f}   "
              f"wall = {res['wall_s']} s")

    # ---- Preregistered pass criteria ----
    # (i) vs Target I at the same L
    combined = []
    pass_i = True
    for r in rows:
        ri = i_by_l[r["L"]]
        d = abs(r["ratio"] - ri["ratio"]) / max(
            1e-9, 2.0 * math.sqrt(r["ratio_err"] ** 2 + ri["ratio_err"] ** 2))
        combined.append((r["L"], round(d, 3)))
        pass_i = pass_i and d <= 1.0

    # (ii) error shrinkage (largest L in the run; production run includes L=40)
    rmax = max(rows, key=lambda r: r["L"])
    err40 = rmax["ratio_err"]
    pass_j = err40 <= G_L20_RATIO_ERR

    out = {
        "target": "J",
        "script": "bcc/bcc_long_ensemble_cubic.py",
        "protocol": {
            "kernel": "Target G verbatim (bcc_cubic_control.run_one_lattice)",
            "beta": cg.BETA,
            "therm_sweeps": THERM_SWEEPS,
            "meas_sweeps": MEAS_SWEEPS,
            "ape": f"alpha={cg.APE_ALPHA} x {cg.APE_STEPS} steps (cubic staple /4)",
            "seed_offset": SEED_OFFSET,
            "bootstrap": cg.B_BOOTSTRAP,
        },
        "rows": rows,
        "delta_vs_target_I": {f"L{L}": {"delta": round(r["ratio"] - i_by_l[L]["ratio"], 3),
                                        "d_combined_sigma": d}
                              for (L, d), r in zip(combined, rows)},
        "pass_i_universality_large_L": bool(pass_i),
        "pass_ii_error_shrinkage": bool(pass_j),
        "pass_ii_detail": {f"L{rmax['L']}_err": err40, "G_L20_err": G_L20_RATIO_ERR},
        "all_pass": bool(pass_i and pass_j),
        "total_wall_s": round(time.time() - t_start, 1),
    }
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "long_ensemble_cubic.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2)

    print("\n" + "=" * 78)
    print("TARGET J SUMMARY")
    for (L, d), r in zip(combined, rows):
        print(f"  L={L}: cubic {r['ratio']:.3f} +- {r['ratio_err']:.3f}  "
              f"vs BCC {i_by_l[L]['ratio']:.3f}  delta = "
              f"{r['ratio'] - i_by_l[L]['ratio']:+.3f} ({d} x combined)")
    print(f"  (i) universality at large L:  {'PASS' if pass_i else 'FAIL'}")
    print(f"  (ii) L{rmax['L']} error {err40:.3f} <= {G_L20_RATIO_ERR}: "
          f"{'PASS' if pass_j else 'FAIL'}")
    print(f"  artifact: {dst}  (total wall {out['total_wall_s']} s)")
    print("=" * 78)


if __name__ == "__main__":
    main()
