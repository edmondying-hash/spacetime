#!/usr/bin/env python3
"""
Shared Preregistered Configuration for the 3D BCC (8-Diagonal) Spacetime Network.

Single source of truth for:
  1. Fixed CODATA 2018 physical constants (never knobs).
  2. Open Decision OD1 (`HOP` switch: `'sqrt3_lP'` vs. `'lP'`) and derived lattice units.
  3. Complete `DECLARED_KNOBS` registry across all 6 subdirectories (`bcc/`, `serverside/`,
     `sr/`, `gr/`, `cosmo/`, `elements/`) plus a `knob(name)` lookup helper.
"""

import math
import os
from typing import Any, Dict, Tuple

# ---------------------------------------------------------------------------
# 1. Fixed Physical Constants (CODATA 2018 exact / recommended) — NEVER KNOBS
# ---------------------------------------------------------------------------
C_LIGHT: float = 299_792_458.0          # m/s (exact)
G_NEWTON: float = 6.67430e-11           # m^3 kg^-1 s^-2
HBAR: float = 1.054571817e-34           # J s
L_PLANCK: float = math.sqrt(HBAR * G_NEWTON / (C_LIGHT ** 3))   # ~1.616255e-35 m
T_PLANCK: float = L_PLANCK / C_LIGHT                            # ~5.391247e-44 s
V_PLANCK: float = L_PLANCK ** 3                                 # ~4.22172e-105 m^3

# ---------------------------------------------------------------------------
# 2. OD1 — Hop-Length Convention Switch (env BCC_HOP overrides default)
#   'sqrt3_lP' : 1 BCC link = sqrt(3) l_P  (coord unit = l_P, Voronoi cell = 4 V_P)
#   'lP'       : 1 BCC link = 1.0 l_P      (coord unit = l_P/sqrt(3), cell = 0.7698 V_P)
# ---------------------------------------------------------------------------
HOP: str = os.environ.get("BCC_HOP", "lP")


def hop_derived(hop: str = "") -> Dict[str, Any]:
    """Compute exact lattice geometry and tick duration enforcing v_hop = c."""
    active_hop = hop or HOP
    if active_hop == "sqrt3_lP":
        hop_len_lp = math.sqrt(3.0)
    elif active_hop == "lP":
        hop_len_lp = 1.0
    else:
        raise ValueError(f"HOP must be 'sqrt3_lP' or 'lP', got '{active_hop}'")

    coord_unit_lp = hop_len_lp / math.sqrt(3.0)
    return {
        "HOP": active_hop,
        "hop_length_lP": hop_len_lp,
        "hop_length_m": hop_len_lp * L_PLANCK,
        "coord_unit_lP": coord_unit_lp,
        "cell_volume_VP": 4.0 * (coord_unit_lp ** 3),
        "tick_tP": hop_len_lp,
        "tick_s": hop_len_lp * T_PLANCK,
        "hop_speed_over_c": 1.0,
        "coords_per_tick_at_c": math.sqrt(3.0),
    }


DERIVED: Dict[str, Any] = hop_derived()

# ---------------------------------------------------------------------------
# 3. DECLARED_KNOBS — Every hand-chosen model parameter across the repository
#    Format: "key": (value, "classification and physical role")
# ---------------------------------------------------------------------------
DECLARED_KNOBS: Dict[str, Tuple[Any, str]] = {
    # Paper-level declared parameters
    "phi0": (1.4, "paper declared knob"),
    "load_factor": (0.5, "paper declared knob"),

    # bcc/ (Microscopic QCD, Confinement & Huygens Wavefront)
    "max_node_ticks": (100.0, "node throughput cap per cycle"),
    "link_weight_mev": (198.0, "baryon MeV per 3-quark Steiner link (tuned)"),
    "baryon_bare_ticks": ("12 + 91*n_s", "baryon bare quark term (tuned)"),
    "baryon_spin_factors": ("N -1, Delta 1, Lambda -1, Sigma -0.5, Xi -0.66, Sigma* 0.8, Xi* 0.56, Omega 0.34", "tuned"),
    "baryon_spin_scale": ("6.5 - 1.4*n_s", "tuned"),
    "redraw_probs": ("u,d 0.72; s 0.40; c 0.18; b 0.08", "hop probability per cycle by flavor"),
    "glueball_formula": ("165 + 362.5*L MeV", "inserted glueball mass formula (tuned)"),
    "lensing_queue": ("util = load*M*0.24/r, delay = u/(1-u)*0.18", "inserted 1/r queue law"),
    "huygens_dt": (0.55, "leapfrog wave step; sets analytic speed dt/sqrt(2) = 0.3889 coord/tick"),
    "huygens_util_cap": (0.65, "max congestion in Huygens c_eff"),
    "huygens_arrival_threshold": (0.15, "|u|*r wavefront arrival trigger"),
    "huygens_load_strength": ("GridMass/938*6.5", "inserted 1/r load scale"),
    "TICK_TO_MEV": (5.0, "meson & nuclear routing tick-to-MeV scale (tuned)"),
    "QUARK_BARE_TICKS": ("l 15.5, s 24.25, c 77.5, b 236.5", "meson bare quark ticks (tuned)"),
    "meson_route_rule": ("3*bare + min(b_avg-2mu, 3.5*b_min)", "two-body reduced-mass routing rule (tuned)"),
    "meson_hyperfine": ("32 * (-3|+1) * b_l^2/(b1*b2)", "hyperfine spin splitting rule (tuned)"),
    "TICKS_PER_LP": (9.0, "gluon flux-tube ticks per l_P of tube length"),
    "string_break_mev": (275.0, "color-singlet q-qbar string breaking threshold"),
    "dirac_mass_coin_theta": (0.25, "Dirac-4 rest-mass coin angle per tick"),

    # serverside/ (Quantum State Bus & Decoherence)
    "orbital_coupling": ("k from core mass", "c_eff = 1/(1+k/r) inserted"),
    "vacuum_noise_prob": ("0..0.06", "per-hop server decoherence probability"),

    # gr/ (General Relativity)
    "node_cap": (100.0, "macroscopic congestion cap C"),
    "r_s_lattice": (3.0, "Schwarzschild radius in BCC coord units"),
    "W_to_g00_map": ("dtau/dt = sqrt(1 - W/C)", "inserted congestion-to-metric map (OD2)"),
    "kugelblitz_ring": ("radius 12, overlap width 0.85", "radiation-seeded horizon geometry"),

    # cosmo/ (Baryogenesis, Dark Sector & CMB)
    "baryo_step_factor_21": (0.5, "Gen2->Gen1 CP step factor relative to Gen3->Gen2"),
    "void_expand_thresh": (20.0, "idle-node congestion gate threshold (W < 20)"),
    "h_vac_rate": (0.01, "late-time void expansion rate per tick"),
    "Omega_m0_Omega_L0": ((0.315, 0.685), "Planck 2018 present matter/vacuum fractions"),
    "halo_profile": ("M_dark ~ r - r_c atan(r/r_c), r_c = 3", "cored loop-halo mass profile"),
    "baryon_profile": ("1200*(1 - exp(-r/1.8))", "exponential galactic disk profile"),
    "T_recomb_z_recomb": ((2994.775, 1098.0), "recombination temp & redshift (T0 = 2.725 K)"),
    "cmb_r_s_d_A_mpc": ((144.43, 13872.0), "sound horizon & angular diameter distance (Mpc)"),
    "cmb_phase_shift": (0.2709, "acoustic phase shift setting l_1 = 220.00 (tuned)"),

    # elements/ (Relativistic Thermal Scaling)
    "hg_lindemann_melt": (0.0301, "Mercury Lindemann k_B*T_melt / E_coh scaling ratio"),
    "hg_trouton_boil": (0.0810, "Mercury Trouton k_B*T_boil / E_coh scaling ratio"),
    "hg_inert_pair_exp": (8.33, "closed-shell 6s^2 relativistic screening exponent"),
}


def knob(name: str) -> Any:
    """Return the raw parameter value for a declared knob name."""
    if name not in DECLARED_KNOBS:
        raise KeyError(f"Undeclared knob '{name}'. Register it in bcc_config.DECLARED_KNOBS first.")
    return DECLARED_KNOBS[name]


if __name__ == "__main__":
    print("=" * 76)
    print("3D BCC SPACETIME NETWORK: PREREGISTERED CONFIGURATION AUDIT")
    print("=" * 76)
    for mode in ("sqrt3_lP", "lP"):
        d = hop_derived(mode)
        print(
            f"  HOP='{mode:<8}' -> link={d['hop_length_lP']:.4f} l_P, "
            f"cell={d['cell_volume_VP']:.4f} V_P, tick={d['tick_tP']:.4f} t_P, v_hop={d['hop_speed_over_c']}c"
        )
    print("-" * 76)
    print(f"Total Declared Knobs Registered: {len(DECLARED_KNOBS)}")
