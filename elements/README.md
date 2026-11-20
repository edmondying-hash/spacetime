# Emergent Atomic Elements, Nuclear Reactions & Molecular Chemistry (`elements/`)

This directory bridges the microscopic **3D BCC Quark–Gluon Lattice (`bcc/`)** into atomic physics, nuclear fusion/fission, relativistic heavy metals, the complete 118-element periodic table, and covalent chemistry.

---

## Core Atomic & Molecular Mechanisms on the 3D BCC Lattice

1. **Generic 118-Element Periodic Table Engine (`bcc_periodic_table.py` & `plot_periodic_dashboard.py`):**
   - Computes quark census (`up` vs. `down`), `4.66`-link BCC gluon Steiner mass share (`~98.85%`), Semi-Empirical Mass Formula (SEMF) nuclear binding energy (`26Fe` peak), Pauli/Madelung shell filling (`1s`–`7p`), Slater screening ($Z_{\text{eff}}$), and relativistic $1s$ Lorentz contraction across **all 118 elements ($Z = 1\dots 118$)**.
2. **Hydrogen Atom & Full Phase Ladder (`bcc_hydrogen_atom.py`):**
   - Breaks down Hydrogen (`98.99%` gluon Steiner tree, `0.96%` valence quarks, `0.054%` electron spinor), Bohr standing-wave spectral lines (`656.1 nm` H-alpha), and thermal phases from Solid $\text{H}_2$ (`<14.01 K`) $\to$ Liquid $\text{H}_2$ (`14.01–20.28 K`) $\to$ Ionized Plasma (`12,000 K`).
3. **Nuclear Fusion & Quantum Tunneling (`bcc_nuclear_fusion.py`):**
   - Contrasts `1/r` virtual-photon Coulomb repulsion against short-range pion/gluon Steiner tree merging (`-40.7 MeV` Helium-4 well), showing why `D + T -> He-4 + n + 17.59 MeV` ignites at `~150M K` via Gamow tunneling while pure `p + p` is bottlenecked by a virtual $W^+$ quark flip.
4. **Nuclear Fission & Chain Reactions (`bcc_nuclear_fission.py`):**
   - Tracks the nuclear binding curve from `2H` up to **`56Fe` (`8.79 MeV/nuc`)** and down to fissile **`235U` (`7.59 MeV/nuc`)**, simulating thermal neutron splitting (`202.5 MeV = 40.5` BCC ticks) and $k_{\text{eff}}$ chain-reaction generations (`0.85`, `1.00`, `1.18`).
5. **Relativistic Mercury & Multi-Electron Shells (`bcc_relativistic_mercury.py` & `bcc_multi_electron_atoms.py`):**
   - Shows how Mercury's (`80Hg`) $+80$ proton core accelerates inner $1s$ electrons to **`0.5838c` ($\gamma = 1.2317$, `18.81%` Lorentz contraction)**, pulling its closed $6s^2$ valence pair into the core so it melts at **`234.32 K`** (room-temperature liquid metal) and turns superconducting below **`4.15 K`**.
6. **Covalent Molecular Chemistry (`bcc_molecular_chemistry.py`):**
   - Shows **Methane (`CH4`)** locking into the exact `109.47°` tetrahedral body diagonals of the 3D BCC unit cell (`0.00 D` dipole, `111.7 K` boiling point), while **Water (`H2O`)**'s two lone pairs compress its `O-H` angle to **`104.45°`** (`1.85 D` dipole, `0.21 eV` H-bonds), keeping Water liquid across **`273.15–373.15 K`**.

---

## Directory Structure & Quick Start (`elements/`)

| File | Description | Run Command |
| :--- | :--- | :--- |
| `bcc_periodic_table.py` | Generic 118-element engine (`Z = 1..118`) with `--element`, `--range`, `--all`, and `--json` export. | `python3 bcc_periodic_table.py --all --json periodic_118.json` |
| `plot_periodic_dashboard.py` | Renders the 4-panel 118-element periodic dashboard (`periodic_dashboard.png`). | `python3 plot_periodic_dashboard.py` |
| `bcc_hydrogen_atom.py` | Hydrogen quark/gluon/electron breakdown, Bohr lines, and `10 K -> 100,000 K` phase ladder. | `python3 bcc_hydrogen_atom.py` |
| `bcc_nuclear_fusion.py` | Coulomb wall vs. gluon Steiner merge, Gamow tunneling, and `D-T` vs. `p-p` fusion channels. | `python3 bcc_nuclear_fusion.py` |
| `bcc_nuclear_fission.py` | `2H -> 56Fe -> 235U` binding curve, thermal neutron split (`202.5 MeV`), and $k_{\text{eff}}$ chain reaction. | `python3 bcc_nuclear_fission.py` |
| `bcc_relativistic_mercury.py` | Relativistic $1s$ contraction (`18.81%`), `79Au` vs. `80Hg` valence comparison, and `2 K -> 700 K` phases. | `python3 bcc_relativistic_mercury.py` |
| `bcc_multi_electron_atoms.py` | Compares `1H`, `4He` (`2.17 K` superfluid), and `12C` (`3,915 K` solid) nuclear & shell properties. | `python3 bcc_multi_electron_atoms.py` |
| `bcc_molecular_chemistry.py` | Models `CH4` (`109.47°` BCC tetrahedral), `H2O` (`104.45°` dipole), and `CO2` covalent chemistry. | `python3 bcc_molecular_chemistry.py` |
