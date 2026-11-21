# Preregistered Lattice Parameters & Falsifiable Benchmark Manifesto

**Date Locked:** November 20, 2026  
**Framework:** Client–Server 3D BCC (8-Diagonal) Spacetime Network  
**Single Source of Truth:** `bcc_config.py`

---

## 1. Purpose & Scientific Discipline
To transition this computational model from an exploratory hypothesis into a falsifiable framework, all fundamental physical constants, open architectural switches, and declared model knobs are locked in `bcc_config.py` prior to running cross-domain benchmarks. No per-domain parameter retuning is permitted when evaluating out-of-sample observables.

---

## 2. Locked Architectural Switches & Core Parameters (`bcc_config.py`)

| Parameter | Locked Value | Classification | Physical Role |
| :--- | :---: | :---: | :--- |
| `C_LIGHT`, `G_NEWTON`, `HBAR` | CODATA 2018 exact | **Fixed Constant** | Defines `L_PLANCK`, `T_PLANCK`, `V_PLANCK` (never tuned) |
| `HOP` (`OD1`) | `'lP'` (locked default) | **Locked Convention** | 1 BCC diagonal hop = `1.0 l_P`, 1 tick = `1.0 t_P`, Voronoi cell = `0.7698 V_P`, $v_{\text{hop}} = c$ |
| `max_node_ticks` / `node_cap` | `100.0` ticks/cycle | **Declared Knob** | Maximum node throughput before horizon deadlock / halo core saturation |
| `link_weight_mev` | `198.0` MeV/link | **Declared Knob** | 3-quark Steiner tree routing energy per BCC diagonal hop |
| `TICK_TO_MEV` | `5.0` MeV/tick | **Declared Knob** | Meson & nuclear routing-tick energy conversion scale |
| `TICKS_PER_LP` | `9.0` ticks/$\ell_P$ | **Declared Knob** | Gluon flux-tube linear energy density (`77.94 MeV/hop` under `sqrt3_lP`) |
| `string_break_mev` | `275.0` MeV | **Declared Knob** | Color-singlet $q\bar{q}$ pair-creation threshold (4-hop snap) |
| `huygens_dt` | `0.55` | **Declared Knob** | Leapfrog wave step (analytic vacuum phase speed = $0.3889\text{ coord/tick}$) |
| `void_expand_thresh` | `20.0` ticks | **Declared Knob** | Congestion gate below which idle vacuum cells insert (`W < 20`) |
| `cmb_phase_shift` | `0.2709` | **Declared Knob** | Recombination acoustic phase offset ($\ell_1 = 220.00$) |

---

## 3. Preregistered Pass/Fail Acceptance Criteria (`run_all_benchmarks.py`)

Every commit to the repository must pass all 13 quantitative assertions without modifying `bcc_config.py`:

1. **Microscopic QCD, Confinement & Emergent Glueball Gap (`bcc/`):**
   - Nucleon (`uud`) mass within `927.3 ± 5.0 MeV` (`~4.66` average Steiner links).
   - Non-Abelian `SU(2)` 4-link BCC rhombus Monte Carlo yields emergent Creutz string tension $\chi(2,2) > 0.15$ while Abelian `U(1)` QED deconfines ($\chi(2,2) < 0.06$ at $\beta = 2.1$).
   - **Target B (Zero-Knob Glueball Mass Gap):** APE-smeared $2\times 2$ blocked BCC rhombus correlators yield $a \cdot m_{0^{++}} > 1.5$ and dimensionless ratio $m_{0^{++}} / \sqrt{\sigma} > 2.5$ (`~1306 MeV` at $\sqrt{\sigma} = 440\text{ MeV}$) with zero inserted formula.
2. **Non-Local Server Bus & Lazy Evaluation (`serverside/`):**
   - Lazy two-cone handshake saves $> 98.0\%$ of 3D grid updates over eager wave propagation.
3. **Special & General Relativity (`sr/`, `gr/`):**
   - Invariant rest mass $m_0 = 927.3000\text{ MeV}$ across $\beta \in [0, 0.99]$.
   - 3D BCC Poisson light deflection equals $2.00 \times$ Newtonian $g_{00}$ deflection (`< 0.5%` error).
4. **Cosmology & Zero-Knob Baryogenesis (`cosmo/`):**
   - PDG 2024 CKM Jarlskog invariant $J = (3.12 \pm 0.15) \times 10^{-5}$; $N = 2$ generations yields $0$ surviving matter.
   - **Target A (Zero-Knob Topological CP Bias):** Counting the `192/512` (`3/8`) non-planar chiral 3-hop twists on the 8-diagonal BCC lattice $\times 3$ spatial axes $\times 2$-step electroweak loop yields $\varepsilon_{3\text{D}} = 2.8384 \times 10^{-5}$, predicting $\eta = 5.8982 \times 10^{-10}$ (within `5%` of Planck 2018's $6.10 \times 10^{-10}$ without fitting).
   - First-order $W = 20 \to 10$ congestion freeze-out locks in $\eta \in [5.0 \times 10^{-10}, 7.0 \times 10^{-10}]$.
   - Cosmic deceleration flips to acceleration at $z_{\text{acc}} = 0.632 \pm 0.02$; CMB first peak at $\ell_1 = 220.0 \pm 1.0$.
5. **118-Element Periodic Engine & Relativistic Chemistry (`elements/`):**
   - Iron (`26Fe`) achieves maximum SEMF nuclear binding per nucleon (`> 8.80 MeV/nuc`).
   - Mercury (`80Hg`) inner $1s$ speed $\beta = 0.5838 \pm 0.001$ and Lorentz contraction $18.81 \pm 0.10\%$.
