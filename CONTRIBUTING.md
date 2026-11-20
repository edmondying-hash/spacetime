# Contributing to the 3D BCC Spacetime Network

Thank you for exploring and testing this open-source physics framework! To keep every contribution reproducible and scientifically transparent, please follow these three steps:

1. **Respect the Preregistered Parameter Lock (`bcc_config.py`):**
   - Do not retune parameters in `bcc_config.py` to fit individual observables.
   - Any new model knob must be registered in `bcc_config.DECLARED_KNOBS` and documented in `PREREGISTRATION.md`.

2. **Run the Automated CI Suite Before Opening a PR:**
   ```bash
   python3 run_all_benchmarks.py
   ```
   All 26 simulation scripts and 11 preregistered physics assertions must pass (`0` errors).

3. **High-Priority Open Research Targets (Zero New Knobs Preferred):**
   - **Continuum Lattice Scaling (`bcc/bcc_confinement_wilson.py`):** Scale the 4-link BCC rhombus Monte Carlo from `8^3` `SU(2)` up to `12^3` and `16^3` full `SU(3)` link matrices to track $m_{0^{++}} / \sqrt{\sigma}$ toward continuum Lattice QCD (`~3.55`).
   - **Bare Quark Tick Weights (`bcc/bcc_meson_sim.py`):** Derive light-quark bare tick weights (`15.5` ticks) directly from discrete chiral symmetry breaking on the 8-diagonal BCC graph.
   - **CMB Acoustic Phase Offset (`cosmo/bcc_cmb_spectrum.py`):** Derive the recombination phase offset (`0.2709`) from discrete photon-baryon diffusion on the BCC lattice.
