#!/usr/bin/env python3
"""
D1 AUDIT: The hadron energy dictionary in pure tick units (`bcc/bcc_tick_energy_audit.py`).

D1 (THEORY.md roadmap) asks whether the whole hadron/nuclear mass sector is
expressible as  tick_structure x kappa  with ONE energy-scale constant kappa.
This audit decomposes every hadron mass in the model into its tick terms and the
IMPLICIT kappa each sector presumes, WITHOUT refitting anything:

  * Meson sector (`bcc/bcc_meson_sim.py`):
        ModelMeV = (bare_t + route_t + spin_t) * TICK_TO_MEV   [kappa = 5.0, explicit]
  * Baryon sector (`bcc/bcc_unified_engine.py`):
        GridMass = bare_t + links*198 + spin_t                 [tick terms added as raw
                                                              MeV  ->  implicit kappa = 1.0]

Findings are reported as facts (per-hadron table + the kappa-consistency test +
the two candidate single-kappa re-expressions). The audit makes no physical
claims beyond the arithmetic; the anchor decision (which measured scale fixes
kappa) is preregistered separately (see PREREGISTRATION.md, D1 fork A/B).

No new knobs; bcc_config.py is not modified.
"""

import json
import os
import sys
from typing import Any, Dict, List

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(_ROOT))

import bcc_config as cfg
from bcc_unified_engine import BCCUnifiedEngine, BARYON_FAMILIES
from bcc_meson_sim import BCCMesonSim, MESON_CATALOG, QUARK_BARE_TICKS

# Reference (PDG 2024) baryon masses, MeV — data inputs, not model knobs
BARYON_PDG_MEV = {
    "N": 938.9, "Delta": 1232.0, "Lambda": 1115.68, "Sigma": 1189.37,
    "Xi": 1314.86, "SigmaStar": 1385.0, "XiStar": 1530.0, "Omega": 1672.45,
}

TICK_TO_MEV_MESON = cfg.DECLARED_KNOBS["TICK_TO_MEV"][0]        # 5.0 (explicit in meson sector)
LINK_WEIGHT_MEV_BARYON = cfg.DECLARED_KNOBS["link_weight_mev"][0]  # 198.0 (MeV per link, baryon sector)


def audit_mesons() -> List[Dict[str, Any]]:
    sim = BCCMesonSim()
    rows = []
    for item in MESON_CATALOG:
        r = sim.evaluate_meson(*item)
        total_ticks = r["BareT"] + r["RouteT"] + r["SpinT"]
        rows.append({
            "sector": "meson", "name": r["name"], "quarks": r["quarks"], "J": r["J"],
            "bare_t": r["BareT"], "route_t": r["RouteT"], "spin_t": r["SpinT"],
            "total_ticks": round(total_ticks, 2),
            "kappa_implicit_mev_per_tick": TICK_TO_MEV_MESON,
            "model_mev": r["ModelMeV"], "pdg_mev": r["PDGMeV"],
            "diff_mev": r["Diff"], "diff_pct": round(100.0 * r["Diff"] / r["PDGMeV"], 2),
        })
    return rows


def audit_baryons() -> List[Dict[str, Any]]:
    engine = BCCUnifiedEngine(size=8,
                              max_node_ticks=cfg.DECLARED_KNOBS["max_node_ticks"][0],
                              link_weight_mev=LINK_WEIGHT_MEV_BARYON)
    rows = []
    for idx, (fam, flv, sp) in enumerate(BARYON_FAMILIES):
        r = engine.simulate_baryon_workload(flv, sp, cycles=3000, seed=42 + idx)
        n_strange = flv.count("s")
        bare_t = 12.0 + 91.0 * n_strange
        spin_t = sp * (6.5 - 1.4 * n_strange)
        links = r["AvgLinks"]
        # The baryon mass adds bare_t and spin_t (tick quantities) directly to MeV:
        # that presumes 1 tick = 1 MeV (implicit kappa = 1.0).
        model_mev = bare_t + links * LINK_WEIGHT_MEV_BARYON + spin_t
        rows.append({
            "sector": "baryon", "name": fam, "flavor": "".join(flv), "spin_factor": sp,
            "avg_links": links,
            "bare_t": round(bare_t, 1), "spin_t": round(spin_t, 2),
            "route_links": links,
            "route_ticks_at_kappa5": round(links * LINK_WEIGHT_MEV_BARYON / TICK_TO_MEV_MESON, 2),
            "route_ticks_at_kappa1": round(links * LINK_WEIGHT_MEV_BARYON, 1),
            "kappa_implicit_mev_per_tick": 1.0,
            "model_mev": round(model_mev, 1), "pdg_mev": BARYON_PDG_MEV[fam],
            "diff_mev": round(model_mev - BARYON_PDG_MEV[fam], 1),
            "diff_pct": round(100.0 * (model_mev - BARYON_PDG_MEV[fam]) / BARYON_PDG_MEV[fam], 2),
        })
    return rows


def single_kappa_test(meson_rows: List[Dict[str, Any]], baryon_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Two candidate single-kappa re-expressions, reported as facts (no refitting)."""
    out: Dict[str, Any] = {}
    n = next(r for r in baryon_rows if r["name"] == "N")
    pi = next(r for r in meson_rows if r["name"] == "pi")

    # (a) kappa = 5.0 (declared TICK_TO_MEV): baryon route re-expressed in ticks
    #     (198 MeV/link -> 39.6 ticks/link), tick terms kept, everything x 5.
    n_k5 = (n["route_ticks_at_kappa5"] + n["bare_t"] + n["spin_t"]) * TICK_TO_MEV_MESON
    pi_k5 = (pi["total_ticks"]) * TICK_TO_MEV_MESON
    out["kappa_5"] = {
        "nucleon_mev": round(n_k5, 1),
        "nucleon_shift_pct": round(100.0 * (n_k5 - n["model_mev"]) / n["model_mev"], 2),
        "pion_mev": round(pi_k5, 1),
        "note": "meson sector unchanged; baryon sector shifts by its route-term re-expression",
    }

    # (b) kappa = 1.0 (implicit baryon scale): meson tick terms x 1
    n_k1 = n["route_ticks_at_kappa1"] * 1.0 + n["bare_t"] + n["spin_t"]
    pi_k1 = pi["total_ticks"] * 1.0
    out["kappa_1"] = {
        "nucleon_mev": round(n_k1, 1),
        "nucleon_shift_pct": round(100.0 * (n_k1 - n["model_mev"]) / n["model_mev"], 2),
        "pion_mev": round(pi_k1, 1),
        "note": "baryon sector unchanged; meson masses collapse by the 5x factor",
    }

    out["conclusion"] = (
        "The meson sector (kappa = 5.0 explicit) and the baryon sector (kappa = 1.0 implicit) "
        "carry a factor-5 energy-scale inconsistency hidden in the tuned constants "
        "(198 MeV/link vs 5 MeV/tick). No single kappa reproduces both sectors with the "
        "current tick structures; unifying the dictionary requires either re-deriving the "
        "tick structures (D3) or a declared rescaling of one sector, plus fixing kappa by "
        "one measured scale (D1 anchor fork A/B)."
    )
    return out


def main() -> None:
    print("=" * 92)
    print("D1 AUDIT: hadron energy dictionary in tick units (no refitting)")
    print("=" * 92)

    mesons = audit_mesons()
    baryons = audit_baryons()

    print("\nMESONS  (ModelMeV = (bare+route+spin) x TICK_TO_MEV; kappa = %.1f explicit)" % TICK_TO_MEV_MESON)
    print(f"{'name':<9}{'J':>2}{'bare_t':>9}{'route_t':>10}{'spin_t':>9}{'tot_ticks':>11}{'model':>10}{'PDG':>10}{'diff%':>8}")
    for r in mesons:
        print(f"{r['name']:<9}{r['J']:>2}{r['bare_t']:>9.2f}{r['route_t']:>10.2f}{r['spin_t']:>9.2f}"
              f"{r['total_ticks']:>11.2f}{r['model_mev']:>10.1f}{r['pdg_mev']:>10.1f}{r['diff_pct']:>8.2f}")

    print("\nBARYONS (GridMass = bare + links*198 MeV + spin; tick terms added raw -> kappa = 1.0 implicit)")
    print(f"{'name':<10}{'links':>8}{'bare_t':>9}{'spin_t':>9}{'route_ticks(k5)':>16}{'model':>10}{'PDG':>10}{'diff%':>8}")
    for r in baryons:
        print(f"{r['name']:<10}{r['avg_links']:>8.2f}{r['bare_t']:>9.1f}{r['spin_t']:>9.2f}"
              f"{r['route_ticks_at_kappa5']:>16.2f}{r['model_mev']:>10.1f}{r['pdg_mev']:>10.1f}{r['diff_pct']:>8.2f}")

    test = single_kappa_test(mesons, baryons)
    print("\nSINGLE-KAPPA CONSISTENCY")
    print(f"  kappa = 5.0: nucleon {test['kappa_5']['nucleon_mev']} MeV "
          f"({test['kappa_5']['nucleon_shift_pct']:+.2f}% vs current), pion {test['kappa_5']['pion_mev']} MeV")
    print(f"  kappa = 1.0: nucleon {test['kappa_1']['nucleon_mev']} MeV "
          f"({test['kappa_1']['nucleon_shift_pct']:+.2f}% vs current), pion {test['kappa_1']['pion_mev']} MeV")
    print(f"  {test['conclusion']}")

    out = os.path.join(_ROOT, "tick_energy_audit.json")
    with open(out, "w") as fh:
        json.dump({"mesons": mesons, "baryons": baryons, "single_kappa_test": test}, fh, indent=2)
    print(f"\nArtifact: {out}")


if __name__ == "__main__":
    main()
