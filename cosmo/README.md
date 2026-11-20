# Emergent Cosmology & Baryogenesis (`cosmo/`)

This directory scales the **3D BCC (8-Diagonal) Spacetime Network** from the earliest electroweak freeze-out window (`~10^-11 s`) up to galactic halos and the Cosmic Microwave Background (CMB) horizon.

---

## Core Cosmological Mechanisms on the 3D BCC Lattice

1. **Zero-Knob 3-Generation Baryogenesis & CKM CP Violation (`bcc_baryogenesis.py`):**
   - Maps Generations 1, 2, and 3 to `1D`, `2D`, and `3D` volumetric BCC routing twists under the `100`-tick node cap (blocking a 4th generation at `128` ticks, matching LEP $N_\nu = 2.984 \pm 0.008$).
   - Proves numerically why $N < 3$ generations yields zero CP violation ($U(2)$ rephases to real; Jarlskog determinant vanishes for degenerate masses).
   - **Zero-Knob Derivation (`Part 5`):** Evaluates all $8^3 = 512$ 3-hop BCC paths, finding exactly **192 non-planar chiral twists** ($192/512 = 3/8$) $\times 3$ spatial axes $\times$ 2-step electroweak loop factor $(\alpha_W / 2\pi)^2$ to derive $\varepsilon_{3\text{D}} = 2.8384 \times 10^{-5}$, predicting **$\eta = 5.8982 \times 10^{-10}$** (`3.31%` from Planck 2018's $6.10 \times 10^{-10}$) with zero fitted knobs.
2. **First-Order BCC Congestion Phase Transition (`bcc_phase_transition.py`):**
   - Couples `bcc_baryogenesis.py` with `bcc_dark_energy.py` across the `W = 20` node-congestion threshold, showing how sudden idle-node vacuum insertion creates an expanding bubble wall ($H/\Gamma$ jumping from `0.21` to `20.09` across $W = 20 \to 10$) that locks in $\kappa_{\text{survival}} \approx 0.95$ (`Sakharov freeze-out`).
3. **Dark Matter Halos as Neutral Closed Gluon Loops ($Q_{\text{EM}} = 0$):**
   - Closed 4-link non-planar BCC gluon rhombus cycles (`1615.0 MeV = 323.0 ticks`) carry zero electromagnetic charge while consuming node processing ticks—flattening galaxy rotation curves (`84.6%` dark fraction), producing Bullet Cluster lensing offsets, and saturating at the `100`-tick node cap to eliminate $1/r$ NFW cusps.
4. **Congestion-Gated Dark Energy & Void Expansion (`bcc_dark_energy.py`):**
   - Idle vacuum insertion ($\approx 0.770\,V_P$ cells) fires only when local workload $W < 20$, keeping bound galaxies ($W = 85$) locked in size while empty voids expand—flipping cosmic deceleration $q(z)$ to acceleration at **$z_{\text{acc}} = 0.632$**.
5. **CMB Redshift Cooling & 3D BCC Acoustic Peak (`bcc_cmb_spectrum.py`):**
   - Stretches recombination photons ($T_{\text{recomb}} = 2994.78\text{ K}$) across $1 + z = 1099$ down to $T_0 = 2.725\text{ K}$ ($n_\gamma = 410.50\text{ cm}^{-3}$, Planck peak at `160.2 GHz`) and places the first acoustic peak at **$\ell_1 = 220.00$** via $c_s = c/\sqrt{3}$.

---

## Directory Structure & Quick Start (`cosmo/`)

| File | Description | Run Command |
| :--- | :--- | :--- |
| `bcc_baryogenesis.py` | PDG 2024 CKM Jarlskog invariant ($J = 3.12 \times 10^{-5}$), $U(2)$ CP proof & zero-knob `3/8` chiral twist derivation of $\eta = 5.90 \times 10^{-10}$. | `python3 bcc_baryogenesis.py` |
| `bcc_phase_transition.py` | First-order $W = 20 \to 10$ congestion bubble wall & Sakharov freeze-out survival sweep. | `python3 bcc_phase_transition.py` |
| `bcc_dark_matter.py` | Invisible gravitational lensing ($Q_{\text{EM}} = 0$), flat rotation curves, and Bullet Cluster collision offsets. | `python3 bcc_dark_matter.py` |
| `bcc_halo_solver.py` | Inverse rotation-curve solver & 100-tick cusp-to-core density saturation. | `python3 bcc_halo_solver.py` |
| `bcc_dark_energy.py` | Congestion-gated galaxy-vs.-void expansion and $z_{\text{acc}} = 0.632$ cosmic acceleration flip. | `python3 bcc_dark_energy.py` |
| `bcc_cmb_spectrum.py` | CMB redshift cooling ($T_0 = 2.725\text{ K}$), Planck blackbody radiance, and $\ell_1 = 220.00$ acoustic peak. | `python3 bcc_cmb_spectrum.py` |
