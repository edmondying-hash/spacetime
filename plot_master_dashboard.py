#!/usr/bin/env python3
"""Root Master Dashboard: Renders a 20-panel (5x4) sectioned chart across all domains."""

import json
import matplotlib.pyplot as plt
import numpy as np


def render_master_dashboard(json_path: str = "master_report.json", out_png: str = "master_dashboard.png") -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pillars = data["pillars"]
    plt.style.use("seaborn-v0_8-darkgrid")
    fig, axes = plt.subplots(5, 4, figsize=(22, 24.5))

    # Color-coded left section banners for each of the 5 rows
    section_banners = [
        ("SECTION 1: [bcc/]\nMicroscopic Lattice,\nQCD & Confinement", "#1d3557"),
        ("SECTION 2: [serverside/]\nQuantum State Bus &\nLazy Handshakes", "#7209b7"),
        ("SECTION 3: [sr/ & gr/]\nSpecial & General\nRelativity", "#2a9d8f"),
        ("SECTION 4: [cosmo/]\nBaryogenesis, Dark\nSector & CMB", "#e07a5f"),
        ("SECTION 5: [elements/]\n118-Element Table,\nFusion & Fission", "#d62828"),
    ]

    # ================= ROW 1: [bcc/] Microscopic Lattice & QCD =================
    ax0, ax1, ax2, ax3 = axes[0]

    mesons = pillars["bcc"]["mesons"]
    names = [m["name"] for m in mesons]
    x = np.arange(len(names))
    ax0.bar(x - 0.18, [m["ModelMeV"] for m in mesons], width=0.36, color="#1d3557", label="3D BCC Model")
    ax0.bar(x + 0.18, [m["PDGMeV"] for m in mesons], width=0.36, color="#e07a5f", label="PDG Data")
    ax0.set_yscale("log")
    ax0.set_xticks(x)
    ax0.set_xticklabels(names, rotation=35, ha="right", fontsize=7.5)
    ax0.set_ylabel("Mass (MeV, log)")
    ax0.set_title("1.1 Ground-State Meson Spectrum", fontweight="bold", fontsize=10)
    ax0.legend(fontsize=7.5)

    ph = pillars["bcc"]["photon_carriers"]
    wk = pillars["bcc"]["weak_carriers"]
    hops = [row["hops"] for row in ph]
    ax1.plot(hops, [row["potential"] for row in ph], marker="o", lw=2.0, color="#219ebc", label="Photon V(r) = 1/r")
    ax1.plot(hops, [row["potential"] for row in wk], marker="s", ls="--", lw=2.0, color="#e63946", label="Weak W/Z (r0 ~ 1.5e17)")
    ax1.set_xlabel("BCC Diagonal Hops")
    ax1.set_ylabel("Carrier Potential V(r)")
    ax1.set_title("1.2 Virtual Carriers: EM vs. Weak", fontweight="bold", fontsize=10)
    ax1.legend(fontsize=7.5)

    gl = pillars["bcc"]["gluon_bundling"]
    g_hops = [row["hops"] for row in gl]
    g_mev = [row["tube_mev"] for row in gl]
    ax2.bar(g_hops, g_mev, color=["#d62828" if r["snapped"] else "#2a9d8f" for r in gl], edgecolor="black")
    ax2.axhline(275.0, color="#1d1e2c", ls="--", lw=1.4, label="Snap Threshold (275 MeV)")
    ax2.set_xlabel("BCC Diagonal Hops")
    ax2.set_ylabel("Tube Energy (MeV)")
    ax2.set_title("1.3 Gluon Bundling & 4-Hop Snap", fontweight="bold", fontsize=10)
    ax2.legend(fontsize=7.5)

    mc_rows = pillars["bcc"]["plaquette_mc"]
    b_lbls = [f"beta={r['beta']}" for r in mc_rows]
    x_mc = np.arange(len(b_lbls))
    ax3.bar(x_mc - 0.17, [r["SU2_non_abelian"]["chi_2x2"] for r in mc_rows], width=0.34, color="#1d3557", label="SU(2) Confined chi(2,2)")
    ax3.bar(x_mc + 0.17, [r["U1_abelian"]["chi_2x2"] for r in mc_rows], width=0.34, color="#a8dadc", label="U(1) Coulomb chi(2,2)")
    ax3.set_xticks(x_mc)
    ax3.set_xticklabels(b_lbls)
    ax3.set_ylabel("Emergent Creutz Tension chi")
    ax3.set_title("1.4 Genuine 3D BCC Plaquette MC", fontweight="bold", fontsize=10)
    ax3.legend(fontsize=7.5)
    # ================= ROW 2: [serverside/] Quantum Bus & Lazy Handshakes =================
    ax4, ax5, ax6, ax7 = axes[1]

    srv = pillars["serverside"]
    noise = srv["noise_per_hop"]
    ax4.plot(noise, srv["ghz_mermin_M"], marker="s", lw=2.0, color="#7209b7", label="3-Particle GHZ (M)")
    ax4.plot(noise, srv["bell_chsh_S"], marker="o", lw=2.0, color="#2a9d8f", label="2-Particle Bell (|S|)")
    ax4.axhline(2.0, color="#d62828", ls="--", lw=1.3, label="Classical Limit (2.0)")
    ax4.set_xlabel("Vacuum Noise / Hop")
    ax4.set_ylabel("Non-Locality Score")
    ax4.set_title("2.1 Bell & GHZ Decoherence", fontweight="bold", fontsize=10)
    ax4.legend(fontsize=7.5)

    lbw = srv["lazy_bandwidth"]
    dts = [r["dt"] for r in lbw]
    ax5.plot(dts, [r["eager_ops"] for r in lbw], marker="^", ls="--", lw=2.0, color="#e63946", label="Eager Full-Grid Updates")
    ax5.plot(dts, [r["lazy_ops"] for r in lbw], marker="o", lw=2.0, color="#7209b7", label="Lazy Two-Cone Handshake")
    ax5.set_yscale("log")
    ax5.set_xlabel("Flight Ticks (dT)")
    ax5.set_ylabel("Lattice Ops (log)")
    ax5.set_title("2.2 Lazy Server Bandwidth Savings", fontweight="bold", fontsize=10)
    ax5.legend(fontsize=7.5)

    fy = srv["fringe_screen_y"]
    ax6.plot(fy, srv["fringe_vac_weights"], marker="o", lw=2.0, color="#7209b7", label="Vacuum (No Fringe Touch)")
    ax6.plot(fy, srv["fringe_air_weights"], marker="s", ls="--", lw=1.8, color="#f4a261", label="300 K Air Fringe Contact")
    ax6.set_xlabel("Detector Screen Y")
    ax6.set_ylabel("Arrival Weight")
    ax6.set_title("2.3 Fringe-Contact Decoherence", fontweight="bold", fontsize=10)
    ax6.legend(fontsize=7.5)

    p3d = pillars["bcc"]["pascal_3d_slice"]
    ax7.plot([r["x"] for r in p3d], [r["p_born"] for r in p3d], marker="o", lw=2.0, color="#3a0ca3", label="3D Integer (N+ - N-)^2")
    ax7.set_xlabel("Central Axis X (y=0, z=0)")
    ax7.set_ylabel("Born Slice Density")
    ax7.set_title("2.4 3D Integer Walk (0.0 Dark Nodes)", fontweight="bold", fontsize=10)
    ax7.legend(fontsize=7.5)

    # ================= ROW 3: [sr/ & gr/] Special & General Relativity =================
    ax8, ax9, ax10, ax11 = axes[2]

    kin = pillars["sr"]["kinematics"]
    betas = [row["beta"] for row in kin]
    ax8.plot(betas, [row["zigzag_gamma"] for row in kin], marker="o", lw=2.0, color="#1d3557", label="Lorentz γ (Time Dilation)")
    ax8.plot(betas, [row["clock_rate"] for row in kin], marker="s", ls="--", color="#e63946", label="Clock Rate (1/γ)")
    ax8.set_xlabel("Velocity Fraction β = v / c")
    ax8.set_ylabel("Dimensionless Factor")
    ax8.set_title("3.1 [sr/] BCC Zigzag Clock Dilation", fontweight="bold", fontsize=10)
    ax8.legend(fontsize=7.5)

    td = pillars["gr"]["time_dilation"]
    r_td = [row["r"] for row in td]
    ax9.plot(r_td, [row["gr_dtau_dt"] for row in td], color="#1d3557", lw=2.2, label="Schwarzschild GR g_00")
    ax9.plot(r_td, [row["bcc_dtau_dt"] for row in td], marker="o", ls="--", color="#e63946", label="3D BCC Poisson Clock")
    ax9.set_xlabel("Radius r (BCC Units)")
    ax9.set_ylabel("Clock Rate dτ / dt")
    ax9.set_title("3.2 [gr/] BCC Poisson Time Dilation", fontweight="bold", fontsize=10)
    ax9.legend(fontsize=7.5)

    ld = pillars["gr"]["light_deflection"]
    b_vals = [row["b"] for row in ld]
    ax10.plot(b_vals, [row["bcc_rad"] for row in ld], marker="o", lw=2.2, color="#2a9d8f", label="3D BCC Total (2.00x Newton)")
    ax10.plot(b_vals, [row["newton_rad"] for row in ld], marker="^", ls="--", color="#f4a261", label="Newtonian (1.00x g_00)")
    ax10.set_xlabel("Impact Parameter b")
    ax10.set_ylabel("Deflection α (rad)")
    ax10.set_title("3.3 [gr/] 2x Einstein Light Deflection", fontweight="bold", fontsize=10)
    ax10.legend(fontsize=7.5)

    pts = np.array(pillars["bcc"]["precessing_orbit_xy"])
    h_rad = pillars["bcc"]["horizon_radius"]
    ax11.add_patch(plt.Circle((0, 0), h_rad, color="#1d1e2c", label=f"Horizon (r={h_rad})"))
    ax11.plot(pts[:, 0], pts[:, 1], color="#f77f00", lw=1.3, label="Precessing Ellipse")
    ax11.set_aspect("equal")
    ax11.set_xlim(-27, 27)
    ax11.set_ylim(-27, 27)
    ax11.set_xlabel("X (BCC Units)")
    ax11.set_ylabel("Y (BCC Units)")
    ax11.set_title("3.4 [gr/] Refractive Orbital Rosette", fontweight="bold", fontsize=10)
    ax11.legend(loc="upper right", fontsize=7.5)
    # ================= ROW 4: [cosmo/] Baryogenesis, Dark Sector & CMB =================
    ax12, ax13, ax14, ax15 = axes[3]

    fo = pillars["cosmo"]["sakharov_freezeout"]
    ax12.plot([r["workload_w"] for r in fo], [r["eta_baryon"] * 1e10 for r in fo], marker="o", lw=2.2, color="#2a9d8f", label="Surviving η (×10⁻¹⁰)")
    ax12.axvline(20.0, color="#d62828", ls="--", lw=1.4, label="W=20 Gate Ignition")
    ax12.axhline(6.1, color="#1d1e2c", ls=":", lw=1.3, label="Planck Target (6.1)")
    ax12.invert_xaxis()
    ax12.set_xlabel("BCC Node Load W (Cooling ->)")
    ax12.set_ylabel("Baryon Ratio η (×10⁻¹⁰)")
    ax12.set_title("4.1 Sakharov W=20->10 Freeze-Out", fontweight="bold", fontsize=10)
    ax12.legend(fontsize=7.5)

    rc = pillars["cosmo"]["rotation_curve"]
    r_rc = [row["r"] for row in rc]
    ax13.plot(r_rc, [row["v_total"] for row in rc], marker="o", lw=2.2, color="#2a9d8f", label="Total (84.6% Dark Halo)")
    ax13.plot(r_rc, [row["v_baryon"] for row in rc], marker="s", ls="--", color="#f4a261", label="Baryons Only")
    ax13.set_xlabel("Galactic Radius r")
    ax13.set_ylabel("Orbital Speed v(r)")
    ax13.set_title("4.2 Flat Galaxy Rotation Curve", fontweight="bold", fontsize=10)
    ax13.legend(fontsize=7.5)

    cc = pillars["cosmo"]["cusp_vs_core"]
    r_cc = [row["r"] for row in cc]
    ax14.plot(r_cc, [row["nfw_cusp_ticks"] for row in cc], marker="^", ls="--", color="#e63946", label="Divergent NFW Cusp")
    ax14.plot(r_cc, [row["grid_core_ticks"] for row in cc], marker="o", lw=2.2, color="#1d3557", label="BCC Cored Halo (<100)")
    ax14.axhline(100.0, color="#1d1e2c", ls=":", lw=1.3, label="Node Cap (100)")
    ax14.set_xlabel("Core Radius r")
    ax14.set_ylabel("Density (ticks/cycle)")
    ax14.set_title("4.3 Cusp-to-Core Saturation", fontweight="bold", fontsize=10)
    ax14.legend(fontsize=7.5)

    de = pillars["cosmo"]["dark_energy_history"]
    z_vals = [row["z"] for row in de]
    ax15.plot(z_vals, [row["omega_m_z"] for row in de], marker="o", color="#e07a5f", label="Matter Ω_m(z)")
    ax15.plot(z_vals, [row["omega_l_z"] for row in de], marker="^", color="#3d5a80", label="Idle Vacuum Ω_Λ(z)")
    ax15.axvline(0.632, color="#2a9d8f", ls=":", lw=1.5, label="Accel Flip (z=0.632)")
    ax15.invert_xaxis()
    ax15.set_xlabel("Redshift z (Past -> Present)")
    ax15.set_ylabel("Cosmic Fraction")
    ax15.set_title("4.4 Congestion-Gated Dark Energy", fontweight="bold", fontsize=10)
    ax15.legend(fontsize=7.5)

    # ================= ROW 5: [elements/] 118-Element Table, Fusion & Fission =================
    ax16, ax17, ax18, ax19 = axes[4]

    p118 = pillars["elements"]["periodic_118"]
    z118 = [row["Z"] for row in p118]
    ax16.plot(z118, [row["bind_per_nucleon_mev"] for row in p118], lw=2.1, color="#1d3557", label="SEMF Bind / Nucleon")
    ax16.axvline(26, color="#2a9d8f", ls="--", lw=1.4, label="26Fe Peak (8.85 MeV)")
    ax16.axvline(92, color="#d62828", ls=":", lw=1.4, label="92U Fissile Cliff")
    ax16.set_xlabel("Atomic Number Z (1..118)")
    ax16.set_ylabel("Binding / Nuc (MeV)")
    ax16.set_title("5.1 118-Element Nuclear Binding", fontweight="bold", fontsize=10)
    ax16.legend(fontsize=7.5)

    ft = pillars["elements"]["fusion_tunneling"]
    ax17.plot([r["temp_mk"] for r in ft], [r["norm_reactivity"] for r in ft], marker="o", lw=2.1, color="#f77f00", label="Gamow Tunneling Rate")
    ax17.axvline(15.0, color="#219ebc", ls=":", lw=1.4, label="Sun Core (15M K)")
    ax17.axvline(150.0, color="#d62828", ls="--", lw=1.4, label="Tokamak (150M K)")
    ax17.set_xlabel("Plasma Temp (Million K)")
    ax17.set_ylabel("Norm Reactivity")
    ax17.set_title("5.2 D-T Fusion Quantum Tunneling", fontweight="bold", fontsize=10)
    ax17.legend(fontsize=7.5)

    fc = pillars["elements"]["fission_chain"]
    gens = [row["gen"] for row in fc]
    ax18.plot(gens, [row["supercritical_k118"] for row in fc], marker="^", lw=2.0, color="#d62828", label="Supercritical (k=1.18)")
    ax18.plot(gens, [row["critical_k100"] for row in fc], marker="s", lw=2.0, color="#2a9d8f", label="Critical (k=1.00)")
    ax18.plot(gens, [row["subcritical_k085"] for row in fc], marker="o", ls="--", lw=1.8, color="#8d99ae", label="Subcritical (k=0.85)")
    ax18.set_xlabel("Fission Generation")
    ax18.set_ylabel("Neutron Count")
    ax18.set_title("5.3 U-235 Fission Chain Reaction", fontweight="bold", fontsize=10)
    ax18.legend(fontsize=7.5)

    ax19_twin = ax19.twinx()
    l_c = ax19.plot(z118, [row["rel_contraction_pct"] for row in p118], lw=2.1, color="#e63946", label="1s Contraction (%)")
    l_z = ax19_twin.plot(z118, [row["z_eff"] for row in p118], lw=1.6, ls="--", color="#7209b7", label="Valence Z_eff")
    ax19.axvline(80, color="#1d1e2c", ls=":", lw=1.3)
    ax19.set_xlabel("Atomic Number Z (1..118)")
    ax19.set_ylabel("1s Contraction (%)", color="#e63946")
    ax19_twin.set_ylabel("Valence Z_eff", color="#7209b7")
    ax19.set_title("5.4 Relativistic Hg & Z_eff Shells", fontweight="bold", fontsize=10)
    lines = l_c + l_z
    ax19.legend(lines, [l.get_label() for l in lines], fontsize=7.5, loc="upper left")

    fig.suptitle(
        "Client-Server 3D BCC Spacetime Network: Sectioned 20-Panel Master Benchmark Dashboard",
        fontsize=17,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.subplots_adjust(left=0.11, top=0.955, hspace=0.38, wspace=0.28)

    # Render color-coded left margin section badges aligned to each row
    for row_idx, (label, badge_color) in enumerate(section_banners):
        bbox = axes[row_idx, 0].get_position()
        y_center = 0.5 * (bbox.y0 + bbox.y1)
        fig.text(
            0.052,
            y_center,
            label,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white",
            bbox={"boxstyle": "round,pad=0.6", "facecolor": badge_color, "edgecolor": "none", "alpha": 0.94},
        )

    plt.savefig(out_png, dpi=180)
    print(f"[Saved sectioned 20-panel master dashboard -> {out_png}]")


if __name__ == "__main__":
    render_master_dashboard()

