# Microscopic 3D BCC Lattice, QCD, Confinement & Spin-1/2 (`bcc/`)

This directory implements the microscopic **3D Body-Centered Cubic (8-Diagonal) Spacetime Lattice**—composed of Planck-scale **truncated octahedron Voronoi cells** (\(\approx 0.770\,V_P\)) with a strict $c = 1$ diagonal hop/tick throughput limit (\(\sqrt{3}\,\ell_P / t_P\)).

---

## Core Microscopic Mechanisms on the 3D BCC Lattice

1. **QCD Hadrons, Glueball Mass Gap & Meson Spectrum (`bcc_unified_engine.py`, `bcc_meson_sim.py`):**
   - Models 3-quark baryons (`uud` proton = `927.3 MeV` via `~4.66`-link BCC Steiner trees), closed 4-link non-planar gluon glueball cycles, all 11 ground-state $q\bar{q}$ mesons (`0.1–15.9 MeV` from PDG), and 4-hop string breaking (`275 MeV` threshold).
2. **Color Confinement & Zero-Knob $0^{++}$ Glueball Mass Gap (`bcc_confinement_wilson.py`):**
   - Contrasts deconfined QED perimeter scaling ($W \sim e^{-m \cdot \text{Perim}}$) against confining non-Abelian Area Law scaling ($W \sim e^{-\sigma \cdot \text{Area}}$), extracts $\sigma_{\text{BCC}} = 77.94\text{ MeV/hop}$ via Creutz double ratios, evaluates the Cornell potential, and runs **genuine Metropolis updates on 4-link BCC rhombus plaquettes** proving non-Abelian $\mathrm{SU}(2)$ spontaneously locks into $\chi(2,2) > 0$ while commuting $\mathrm{U}(1)$ deconfines ($\chi \to 0$).
   - **Zero-Knob $0^{++}$ Glueball Mass Gap (`Part 5`):** Extracts the scalar $0^{++}$ glueball mass gap ($a \cdot m = 1.9242$, $m_{0^{++}}/\sqrt{\sigma} = 2.968$, **$1306.1\text{ MeV}$** at $\sqrt{\sigma} = 440\text{ MeV}$) directly from APE-smeared $2\times 2$ blocked BCC rhombus correlator decay with zero inserted mass formula.
3. **Virtual Force Carriers & 3D FFT Green's Functions (`bcc_virtual_carriers.py`):**
   - Ties Yukawa range to Compton wavelength $r_0 = \hbar / (m c)$ and solves the genuine static Green's function on the 8-link BCC graph via 3D FFT, recovering $G(r) = 1/(4\pi r)$ and exponential Yukawa screening directly from the discrete Laplacian.
4. **3D Dual-Channel Integer Pascal Walk & Born Rule (`bcc_dual_pascal_born.py`):**
   - Routes pure integer phase channels $(N_+, N_-)$ across all **8 BCC body diagonals** $(\pm 1, \pm 1, \pm 1)$, carving exact $0.00000$ 3D dark nodes ($N_+ - N_- = 0$) and converging $(N_+ - N_-)^2$ directly to the continuous 3D wave-equation probability density $|\psi(x, y, z)|^2$.
5. **Dirac-4 Spinors, Refractive Orbits & Tabletop Bench (`bcc_dirac4_spinor.py`, `bcc_orbital_sim.py`, `bcc_workbench_interferometer.py`):**
   - Models 4-component `Dirac-4` spinors ($720^\circ$ double cover and Zitterbewegung jitter), refractive wavepacket perihelion precession, and a tabletop `976 nm` diode + torsion pendulum + interferometer test.

---

## Directory Structure & Quick Start (`bcc/`)

| File | Description | Run Command |
| :--- | :--- | :--- |
| `bcc_unified_engine.py` | 5-module core engine (baryons, glueball gap, lensing, horizons, double-slit, isotropy). | `python3 bcc_unified_engine.py` |
| `bcc_meson_sim.py` | 11 ground-state $q\bar{q}$ mesons ($\pi \dots \Upsilon$) & 4-hop BCC string breaking. | `python3 bcc_meson_sim.py` |
| `bcc_confinement_wilson.py` | Wilson Area vs. Perimeter law, Creutz ratios, Cornell $V(R)$, $\mathrm{SU}(2)$ vs. $\mathrm{U}(1)$ MC & zero-knob $0^{++}$ glueball gap. | `python3 bcc_confinement_wilson.py` |
| `bcc_virtual_carriers.py` | Compton Yukawa carrier ranges & genuine 3D FFT lattice Green's functions ($\mu=0$ & $\mu>0$). | `python3 bcc_virtual_carriers.py` |
| `bcc_dual_pascal_born.py` | 8-diagonal 3D integer $(N_+, N_-)$ walk carving 3D dark nodes & converging to $|\psi(x,y,z)|^2$. | `python3 bcc_dual_pascal_born.py` |
| `bcc_dirac4_spinor.py` | 4-component Dirac spinor ($720^\circ$ double cover, Zitterbewegung, 3D BCC walk). | `python3 bcc_dirac4_spinor.py` |
| `bcc_orbital_sim.py` | Refractive wavepacket orbits, perihelion precession & horizon capture. | `python3 bcc_orbital_sim.py` |
| `bcc_workbench_interferometer.py` | Tabletop `976 nm` diode + torsion pendulum + interferometer benchmark. | `python3 bcc_workbench_interferometer.py` |
| `plot_bcc_results.py` | Generates the 4-panel microscopic benchmark dashboard. | `python3 plot_bcc_results.py` |
| `plot_bcc_3d_cell.py` | Renders 4-panel 3D wireframes (unit cell, truncated octahedron $\approx 0.77\,V_P$, Steiner tree, glueball). | `python3 plot_bcc_3d_cell.py` |
| `animate_bcc_quarks.py` | Generates an animated 3D GIF of hopping quarks & dynamic Steiner flux trees. | `python3 animate_bcc_quarks.py` |
