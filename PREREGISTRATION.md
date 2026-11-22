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
6. **Target F (Lattice-Size Scaling of the Zero-Knob Glueball Ratio, `bcc/bcc_glueball_scaling.py`):**
   - *Protocol (locked before execution):* Genuine SU(2) Metropolis Monte Carlo on the $4 \times L^3$-link 3D BCC (8-diagonal) lattice at $\beta = 2.15$ (identical to Target B), parallel single-proposal sweeps with step parameter $0.45$, $2000$ thermalization + $3000$ measurement sweeps per $L \in \{8, 12, 16, 20\}$, fixed seed $2026 + L$. APE link smearing $\alpha = 0.55$, $3$ steps, then the same $2\times 2$ blocked BCC rhombus $0^{++}$ scalar operator as Target B. Connected correlator $C(dt) = \langle O_2\times2(z)\, O_2\times2(z+dt)\rangle_{\text{conn}}$ measured at $dt = 0..5$; mass from $m = -\ln(C(1)/C(0))$. Statistical errors by non-overlapping-sweep bootstrap ($B = 2000$) propagated through $m$, $\chi(2,2)$, and $m/\sqrt{\chi(2,2)}$.
   - *Protocol refinement (Nov 21, before the final run, diagnostic-driven):* a kernel-equivalence diagnostic (L = 6, parallel vs. sequential kernel, 3000 thermalization sweeps, 500 measurements, $\beta = 2.15$) showed that the original 100/400-sweep schedule — and the Target B baseline's 35/90 schedule — is **under-thermalized from the identity start**: $\chi(2,2)$ falls from $0.42$ (35 thermalization sweeps) to $0.305$ (sequential) / $0.331$ (parallel) after 3000 sweeps, and the kernels agree with each other once thermalized. The final ensembles are therefore re-preregistered at 2000/3000 sweeps; the 100/400-sweep results are retained in the artifact as under-thermalized negative artifacts, not as physics.
   - *Pass criteria:*
     - (a) **Kernel validation (completed before the final run, PASS):** the parallel kernel reproduces the sequential Target-B kernel on L = 6, $\beta = 2.15$, 3000 thermalization + 500 measurement sweeps, seed 2026: $\chi(2,2) = 0.3313$ vs. $0.3049$ and $m = 3.4873$ vs. $3.6985$ (sequential), agreeing within 500-sweep bootstrap errors. The 35/90-sweep Target B baseline (ratio 2.968) is identified as under-thermalized and is not used as a validation target.
     - (b) **Convergence:** the $L = 20$ ratio is $\ge 3.20$ (i.e., within $10\%$ of the infinite-volume continuum SU(2) lattice-QCD value $3.55 \pm 0.15$) with bootstrap error $\le 0.15$, and $m/\sqrt{\sigma}(L=20) \ge m/\sqrt{\sigma}(L=8) + 0.10$.
   - *Declared failure path:* if (b) fails, the result is reported as a genuine negative (finite-lattice / UV-residual artifact) and follow-ups (multi-level variational smearing, deeper-blocked operators, full SU(3) gauge group) are to be preregistered here *before* execution.
   - *No new knobs:* $\beta = 2.15$, APE $\alpha = 0.55$/$3$ steps, and the operator definition are inherited verbatim from Target B; `bcc_config.py` is not modified.
7. **Target G (Cubic-3D Control: is the ~5.5 ratio a property of 3D SU(2) gauge dynamics or of BCC geometry?, `bcc/bcc_cubic_control.py`):**
   - *Protocol (locked before execution):* Standard 3D cubic SU(2) Metropolis Monte Carlo (3 link directions, 12 plaquettes per site) with the same gauge coupling $\beta = 2.15$, parallel single-proposal sweeps (step $0.45$), $2000$ thermalization + $3000$ measurement sweeps per $L \in \{8, 12, 16, 20\}$, seed $3000 + L$, APE $\alpha = 0.55$/$3$ steps (staple normalized by the 4 neighboring plaquettes per cubic link, the 3D analogue of the BCC code's $/6$), 2$\times$2 blocked plaquette $0^{++}$ operator, connected $C(dt)$ at $dt = 0..5$, $m = -\ln(C(1)/C(0))$, bootstrap ($B = 2000$).
   - *Decision fork (both branches are valid preregistered outcomes):*
     - (i) **Lattice-universal:** if $m/\sqrt{\sigma}$ of the cubic control equals the Target F BCC value at $L = 20$ within $\sim 2$ combined bootstrap errors, the plateau ($\approx 5.5$) is a property of 3D SU(2) gauge dynamics, and the paper's reference value must be the 3D (not 4D) continuum ratio.
     - (ii) **BCC-specific:** if the two differ beyond $\sim 2$ combined errors, the BCC diagonal geometry shifts the ratio, and the theory must account for the BCC-specific value (the anisotropy/geometry correction is then a prediction in its own right).
   - *Result (Nov 21):* cubic-3D ratio = 4.50 / 4.82 / 4.63 / 5.32 (L = 8/12/16/20, bootstrap errors 0.29–0.95) vs. BCC 5.37 / 5.45 / 5.84 / 5.59; $\Delta_{L=20} = -0.272$ ($0.28\sigma$ combined) $\Rightarrow$ **verdict (i): LATTICE-UNIVERSAL** — the $\approx 5.5$ plateau is a property of 3D SU(2) gauge dynamics; the reference value in the paper must be the 3D continuum ratio, not the 4D $3.55$. Caveat (recorded): the cubic error bars are dominated by marginal $C(1)$ signal-to-noise (bootstrap-biased $-\ln$ estimator); $\chi(2,2)$ itself is lattice-dependent (cubic $\approx 0.71$ vs. BCC $\approx 0.42$ at the same $\beta$), so only the dimensionless ratio is universal. Declared refinement (before execution): a tightened cubic run (multi-level APE or $\ge 6000$ measurement sweeps) to shrink the cubic errors.
8. **Target H (D2 — Genuine Congestion-Queueing Gravity, `gr/bcc_congestion_queueing.py`):**
   - *Audit (drives this target):* the existing `gr/bcc_gr_emergence.py` benchmark is circular — the 2x Einstein deflection is set analytically ($\alpha_{\text{time}} = \alpha_{\text{space}} = r_s/b$ by assignment), the Poisson solver imposes $W = C(r_s/R)$ on its outer boundary (the GR answer), and the time-dilation profile compares $\sqrt{1-W/C}$ against the identical Schwarzschild expression. Target H rebuilds the measurement so nothing GR-shaped is imposed.
   - *Protocol (locked before execution; revised before any H1/H3 result was reported — a dry run showed the original cluster-source $R = 64$ design puts the fit region at 87% of the boundary, distorting the shape; revised to a point source at $R = 128$. H4 was revised once after the first H4 data, for the reason recorded in the H4 bullet below):*
     - **H1 (genuine congestion profile):** steady state of the LOCAL dynamics only: BCC 8-neighbor queue diffusion $W \leftarrow W + D(\overline{W}_{8nb} - W)$ per tick ($D = 0.1$), a sustained POINT source $S = 60$ per tick at the origin (mass = sustained workload injection; steady-state excess $S/D = 600$ ticks on the source node), OPEN boundary $W = 0$ at $R_{\max} = 128$ (spherical; no $1/r$ boundary condition anywhere), $C = 100$. The steady state solves $W - \overline{W}_{8nb} = (S/D)\,\delta_{\text{origin}}$ and is computed EXACTLY on the fundamental $1/48$ octahedral domain ($\approx 48k$ unknowns — the symmetry group of the BCC 8-link geometry), verified independently by evaluating the steady-state residual $|W - \overline{W}_{8nb} - (S/D)\delta_{\text{origin}}|$ on the FULL 3D grid at machine precision ($< 10^{-13}$), and a full-grid Jacobi transient on $R = 64$ (12000 ticks, checkpoints) verifies that the local dynamics monotonically relaxes toward the solved state. The profile $W(r)$ is measured along the axis; $r_s$ is the saturation radius from the fitted line, $A(1/r_s - 1/R_{\max}) = C$.
     - **H2 (preregistered queue maps, tested before looking at deflection):** Map A (M/M/1 residual service): $t_{\text{hop}}(r) = 1/(1-\rho(r))$; Map B (declared OD2): $t_{\text{hop}}(r) = 1/\sqrt{1-\rho(r)}$; $\rho = W/C$ from the H1 measured profile (clipped at 0.999).
     - **H3 (local time dilation):** the clock at $r$ ticks at the local queue rate, so the ratio (local tick / far-field tick) $= 1/\text{map}(\rho(r_{\text{obs}}))$ at $r_{\text{obs}} \in \{2,4,8,16\}\,r_s$, compared with Schwarzschild $\sqrt{1-r_s/r_{\text{obs}}}$. Pre-execution derived expectations: Map B matches within $\sim 2\%$ (residual = the open-boundary term, $\mathcal{O}(r_s/R_{\max})$); Map A gives the Newtonian linear form $1-\rho$ and is expected to FAIL the 5% bound.
     - **H4 (queue-potential integral, revised):** first H4 data (minimum-cost Fermat path) showed that on the finite open grid the least-delay photon detours around the congestion ball at ZERO extra cost — the BCC diagonal hops make the planar light cone an L∞ (chess-king) metric, so any detour to the cutoff radius $R$ costs exactly the flat cost, and the asymptotic deflection is set by the cutoff radius (hard-sphere $2\arcsin(b/R)$), not by the potential. The clean potential-sensitive observable is therefore the transit excess of the FORCED straight-line path, $\Delta(b) = \int [n(r)-1]\, ds$ measured tick-by-tick along $y = -b$, $x \in [-170, 170]$, at $b = \{16, 24, 32\}\,r_s$ (even integers); the minimum-cost detour geometry is reported as a lattice property (with the hard-sphere reference), not as a lens measurement.
   - *Pass criteria (with the pre-execution derived expectations recorded above):*
     - (H1) measured $W(r)$ fits $A(1/r - 1/R_{\max})$ (one free amplitude $A$, zero boundary) within 2% for $r \in [8, 64]$.
     - (H3) Map A or Map B reproduces the Schwarzschild local time dilation within 5% at all four radii $\Rightarrow$ that map is the DERIVED congestion-to-time-dilation map. Recorded expectation: Map B passes, Map A fails.
     - (H4) DERIVED expectation (weak-$\rho$ regime along $b \ge 16\,r_s$, where $n-1 \approx$ linear in $\rho$): Map A gives $n_A - 1 \approx \rho$ (the GR effective-index depth, since the measured $\rho(r) \approx r_s/r$ to the open-boundary factor), Map B gives $n_B - 1 \approx \rho/2$ (half depth, Newtonian). Preregistered pass: $\Delta_A(b)/\Delta_B(b) \in [1.8, 2.2]$ at every $b$. The finite-grid deflection (hard-sphere regime) is NOT used as a criterion — recorded reason above.
   - *No new knobs:* $C = 100$ and the BCC geometry are A1 axioms; $D$, $S$, and the grid are protocol constants locked above; `bcc_config.py` is not modified.
9. **D1 — Single-Scale Energy Dictionary (audit complete; anchor decision pending):**
   - *Audit (completed Nov 21, `bcc/bcc_tick_energy_audit.py`, artifact `bcc/tick_energy_audit.json`):*
     - **Meson sector:** all 11 mesons are $(\text{bare}+\text{route}+\text{spin})_{\text{ticks}} \times 5.0$ within $1.6\%$ of PDG — one consistent $\kappa = 5.0$.
     - **Baryon sector:** `GridMass = bare + links*198 MeV + spin` adds tick terms raw, i.e. an *implicit* $\kappa = 1.0$ — a factor-5 scale inconsistency with the meson sector hidden in the tuned constants ($198\text{ MeV/link}$ vs $5\text{ MeV/tick}$).
     - **Baryon spectrum (new finding):** with the current tick structures only the nucleon fits ($-1.1\%$); the other seven baryons are $9$–$27\%$ below PDG ($\Delta$ $-24.1\%$, $\Lambda$ $-9.4\%$, $\Sigma$ $-14.3\%$, $\Xi$ $-15.0\%$, $\Sigma^*$ $-25.7\%$, $\Xi^*$ $-26.2\%$, $\Omega$ $-27.1\%$). The baryon tick structure (bare $12+91n_s$, spin scale $6.5-1.4n_s$) cannot carry strange-quark mass splittings; re-deriving it (D3) is now a prerequisite, not an option.
   - *Anchor fork (both preregistered, user decides before execution):*
     - **Anchor B (lattice-QCD convention, recommended first):** fix $\kappa$ by the nucleon mass $938.9\text{ MeV}$ (the scale-fixing input); then the 11-meson spectrum and the (re-derived) baryon spectrum are out-of-sample predictions against PDG.
     - **Anchor A (deeper, deferred):** fix $\kappa$ from the measured QCD string tension $\sqrt{\sigma} = 440\text{ MeV}$ matched to the Target F emergent gauge tension — requires resolving the coarse-graining scale (Planck-convention hop vs. hadronic routing length; see THEORY.md F2), so it is declared a sub-project after D3.
   - *Pass criteria (for the executed anchor):* with one fixed $\kappa$ and NO per-hadron retuning, all 11 mesons within $2\%$ of PDG and the re-derived baryon spectrum within $5\%$ (nucleon within $1\%$). Any failed hadron is a declared theory failure of the tick structure, reported as such.
