# Client-Server 3D BCC Spacetime Network

[![Preregistered 3D BCC Benchmarks](https://github.comedmondying-hash/spacetime/actions/workflows/ci.yml/badge.svg)](https://github.comedmondying-hash/spacetime/actions/workflows/ci.yml) [![License: MIT](https://shields.io)](LICENSE)


A computational physics framework modeling spacetime as a **two-tier client-server architecture** built on a uniform, fixed-capacity **3D Body-Centered Cubic (BCC) 8-diagonal crystal lattice** (locked under **`HOP = "lP"`** in `bcc_config.py`: `1` diagonal hop = `1.0000 l_P`, `1` tick = `1.0000 t_P`, hop speed = `1.0c`, and Kelvin truncated-octahedron Voronoi cell volume = `0.7698 V_P`):

- **Client Space (`bcc/`, `sr/`, `gr/`, `cosmo/`, `elements/`):** Observable 3D BCC spatial grid where matter, virtual force carriers, confining gluon flux trees, light waves, clocks, all 118 elements, and galaxies operate under a strict c = 1 diagonal hop/tick throughput limit (\(\ell_P / t_P\)).
- **Server Space (`serverside/`):** Private kernel state-binding tables carried invisibly during `redraw()` ticks, resolving multi-particle entanglement (`Bell`, `GHZ`), lazy two-cone Pascal handshakes (`>99.75%` vacuum bandwidth savings), delayed-choice quantum erasure, fringe-contact decoherence, and anti-FTL scrambling without faster-than-light client signaling.

These programs are toy models built on BCC lattice logic. Matches to measured values come partly from hand-set or calibrated inputs, so they are not independent predictions.

---

## Quick Start: Preregistered CI Suite, Master Report & 20-Panel Dashboard

From the root `spacetime/` directory, verify all 26 scripts and 11 preregistered physics assertions against the locked `bcc_config.py` manifest, export the unified JSON report, and render the 20-panel (`5x4`) sectioned dashboard (`master_dashboard.png`):

```bash
python3 run_all_benchmarks.py
python3 export_master_report.py
python3 plot_master_dashboard.py
```

- **Preregistered Parameter & Falsification Manifest:** [`PREREGISTRATION.md`](PREREGISTRATION.md)
- **Single Source of Truth & Knob Registry:** [`bcc_config.py`](bcc_config.py) (`HOP = "lP"`, SHA-256 audited)

---

## Six-Pillar Repository Structure

```text
spacetime/
├── README.md                        # Top-level unified architecture overview
├── PREREGISTRATION.md               # Locked lattice conventions, 39 declared knobs & 11 CI assertions
├── bcc_config.py                    # Single source of truth (CODATA constants, HOP="lP", knob registry)
├── run_all_benchmarks.py            # Automated CI test suite (26 scripts + 11 preregistered assertions)
├── export_master_report.py          # Unified JSON exporter across all 6 subdirectories
├── plot_master_dashboard.py         # 20-panel (5x4) sectioned dashboard generator (master_dashboard.png)
├── bcc/                             # 1. Microscopic 3D BCC Lattice, QCD, Confinement & Spin-1/2
│   ├── README.md
│   ├── bcc_unified_engine.py        # 5-module engine (baryons, glueball gap, lensing, horizons, double-slit, isotropy)
│   ├── bcc_meson_sim.py             # 11 ground-state q-qbar mesons (pi..Upsilon) & BCC flux-tube string breaking
│   ├── bcc_confinement_wilson.py    # Wilson Area vs. Perimeter law, Creutz ratios, SU(2) vs. U(1) MC & zero-knob 0++ gap
│   ├── bcc_virtual_carriers.py      # Compton Yukawa carrier ranges & genuine 3D FFT lattice Green's functions
│   ├── bcc_dual_pascal_born.py      # 8-diagonal 3D integer (N_+, N_-) walk carving 3D dark nodes & |psi(x,y,z)|^2
│   ├── bcc_dirac4_spinor.py         # 4-component Dirac spinor (720° double cover, Zitterbewegung, 3D BCC walk)
│   ├── bcc_orbital_sim.py           # Refractive wavepacket orbits, perihelion precession & horizon capture
│   ├── bcc_workbench_interferometer.py # Tabletop 976 nm diode + torsion pendulum + interferometer test
│   ├── plot_bcc_results.py          # 4-panel benchmark dashboard generator
│   ├── plot_bcc_3d_cell.py          # 4-panel 3D wireframe (unit cell, truncated octahedron 0.7698 V_P, Steiner tree)
│   └── animate_bcc_quarks.py        # Animated 3D GIF of hopping quarks & dynamic Steiner flux tree
├── serverside/                      # 2. Non-Local Server State Bus, Lazy Handshakes & Firewall
│   ├── README.md
│   ├── lazy_pascal_handshake.py     # Lazy two-cone (forward + inverted backward) handshake & fringe-contact decohere()
│   ├── entangled_bell_server.py     # Spacelike-separated Bell CHSH benchmark (|S| > 2.0, 50/50 marginals)
│   ├── spacetime_server_api.py      # Zero-metadata ClientParticle + 4-primitive kernel API (Bell & GHZ sweeps)
│   ├── quantum_eraser_server.py     # Delayed-choice quantum eraser (complementary fringe / anti-fringe sorting)
│   ├── dense_coding_firewall.py     # Anti-FTL signaling firewall, mid-flight scrambling & 100% 4-state dense coding
│   └── octant_huygens_fast.py       # 8x octant-symmetry continuum convergence (R=60..240 -> 0.056% isotropy error)
├── sr/                              # 3. Special Relativity (Lorentz Kinematics & Dispersion)
│   ├── README.md
│   └── bcc_sr_emergence.py          # BCC zigzag clock gamma, E^2=(pc)^2+(m0c^2)^2 & bounded velocity addition
├── gr/                              # 4. Macroscopic General Relativity (Schwarzschild & Kerr Metrics)
│   ├── README.md
│   ├── bcc_gr_emergence.py          # 3D BCC Poisson relaxation W(r), g_00 time dilation, 2x Einstein deflection & precession
│   ├── bcc_frame_dragging.py        # Kerr g_t_phi azimuthal drag, prograde/retrograde period split & 1/r^3 scaling
│   └── bcc_kugelblitz_spin.py       # Radiation-seeded black hole (W >= 100), recoil ledger & Kerr spin parameter a*
├── cosmo/                           # 5. Emergent Cosmology, Zero-Knob Baryogenesis, Dark Sector & CMB
│   ├── README.md
│   ├── bcc_baryogenesis.py          # PDG 2024 CKM Jarlskog invariant, U(2) CP proof & zero-knob 3/8 chiral twist -> eta
│   ├── bcc_phase_transition.py      # First-order W = 20 -> 10 congestion bubble wall & Sakharov baryon freeze-out
│   ├── bcc_dark_matter.py           # Q_EM=0 BCC 4-link loop halos, flat rotation curves & Bullet Cluster offset
│   ├── bcc_halo_solver.py           # Inverse rotation-curve solver & 100-tick cusp-to-core density saturation
│   ├── bcc_dark_energy.py           # Congestion-gated void expansion & z_acc = 0.632 cosmic acceleration flip
│   └── bcc_cmb_spectrum.py          # CMB redshift cooling (T_0 = 2.725 K), Planck radiance & l_1 = 220.00 peak
└── elements/                        # 6. 118-Element Periodic Engine, Fusion/Fission, Mercury & Chemistry
    ├── README.md
    ├── bcc_periodic_table.py        # Generic 118-element periodic engine (Z = 1..118) with CLI & JSON export
    ├── plot_periodic_dashboard.py   # 4-panel 118-element dashboard (periodic_dashboard.png)
    ├── bcc_hydrogen_atom.py         # Hydrogen quark/gluon/electron breakdown, Bohr lines & 10 K->100,000 K phases
    ├── bcc_nuclear_fusion.py        # Coulomb barrier vs. gluon Steiner merge, Gamow tunneling & D-T vs. p-p fusion
    ├── bcc_nuclear_fission.py       # 2H -> 56Fe -> 235U binding curve, neutron split (202.5 MeV) & k_eff chain reaction
    ├── bcc_relativistic_mercury.py  # Audited DATA/KNOBS/DERIVED relativistic 1s contraction (18.81%) & liquid-metal Hg
    ├── bcc_multi_electron_atoms.py  # 1H, 4He, and 12C pion binding, Pauli shell screening (Z_eff) & phase extremes
    └── bcc_molecular_chemistry.py   # CH4 (109.47° BCC tetrahedral), H2O (104.45° dipole) & CO2 covalent chemistry
```

---

## Unified Physics Summary Across All Six Pillars

| Physics Domain | Directory | Network Mechanism | Preregistered Simulation Benchmark |
| :--- | :---: | :--- | :--- |
| **QCD, Confinement & Glueball Gap** | `bcc/` | $q\bar{q}$ tubes, 3-quark Steiner trees, 4-link $\mathrm{SU}(2)$ rhombus plaquettes & APE-smeared $2\times 2$ correlators | Nucleon = **`929.8 MeV`**; Creutz $\chi(2,2) = \mathbf{0.2678}$; zero-knob $0^{++}$ gap **$m_{0^{++}}/\sqrt{\sigma} = 2.968$ (`1306.1 MeV`)** |
| **3D Integer Interference** | `bcc/` | 8-diagonal integer $(N_+, N_-)$ phase-channel counting & $(N_+ - N_-)^2$ detection workload | Exact `0.00000` 3D dark nodes & smooth convergence to 3D $|\psi(x,y,z)|^2$ across `117,649` nodes |
| **Continuum Isotropy** | `bcc/`, `serverside/` | Multi-path Huygens wavefront spreading across Kelvin truncated-octahedron cells (`0.7698 V_P`) | Spherical anisotropy error drops from `0.840%` ($R=30$) to **`0.056%`** ($R=240$) |
| **Lazy Handshakes & Eraser** | `serverside/` | Unrendered emission tickets (`0` mid-flight updates), fringe-contact `decohere()`, and inverted backward Pascal cones | **`99.751%`** bandwidth savings ($dT=40$), Bell **`|S| = 2.8544`**, GHZ **`M = 4.0000`**, and complementary eraser fringes |
| **No-Signaling Firewall** | `serverside/` | Random outcome injection on `decohere()` + one-time-pad transit scrambling | FTL exploit blocked (`0.4939` noise); 4-state superdense decoding = **`100.0%`** at $v \le c$ |
| **Special Relativity** | `sr/` | Orthogonal split of $c = 1$ hop/tick budget between translation ($\beta$) and internal BCC zigzag clocks | Exact $\gamma = 1/\sqrt{1-\beta^2}$, invariant $m_0 = 927.3000\text{ MeV}$ (`0.00` residual), and bounded $u \oplus v \le c$ |
| **General Relativity** | `gr/`, `bcc/` | 3D BCC Poisson congestion $W(r)/C_{\text{cap}} = r_s/r$, horizon deadlocks, and azimuthal spin curl | Exact **`2.0000x`** Einstein deflection, rosette perihelion precession, Kugelblitz BH & $1/r^3$ Kerr drag |
| **Zero-Knob Baryogenesis & Cosmo** | `cosmo/` | `192/512` (`3/8`) 3D BCC chiral twists $\to \varepsilon_{3\text{D}}$, $W=20 \to 10$ freeze-out, $Q_{\text{EM}}=0$ halos & CMB | Zero-knob **$\eta = 5.898 \times 10^{-10}$** (`3.31%` from Planck), **$z_{\text{acc}} = 0.632$** & **$\ell_1 = 220.00$** |
| **118 Elements & Chemistry** | `elements/` | Periodic `Z=1..118` SEMF binding, Gamow fusion, fission, $Z\alpha$ contraction & $sp^3$ covalent bonds | **`26Fe` peak (`8.846 MeV/nuc`)**, **`80Hg` `18.81%` liquid-metal contraction**, and **`104.45°` liquid $\text{H}_2\text{O}$** |
