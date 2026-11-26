# The 3D BCC Spacetime Network: Axioms, Dictionary & Derivation Roadmap

**Status:** WORK IN PROGRESS — draft scaffold for the theory document.
**Author:** Edmond (with implementation support).
**Companion artifacts:** `PREREGISTRATION.md` (locked protocol), `bcc_config.py` (knob registry),
`bcc/bcc_glueball_scaling.json` + `bcc/cubic_control.json` (Target F/G results).

> The benchmark repository demonstrates *that* the network reproduces quantitative
> physics across six domains. This document states *why*: it fixes the axioms, the
> mass–workload dictionary, and a per-knob derivation roadmap, so that every number
> is either (i) derived from the axioms, (ii) measured by the network, or (iii)
> honestly declared as an input — never hidden.

---

## 1. Axioms of the Network

**A1 — The substrate is a finite-capacity network.**
Space is a 3D Body-Centered Cubic crystal lattice with 8 diagonal links per node
(the dual of the bitruncated cubic honeycomb; space-filling Kelvin truncated-
octahedron Voronoi cells, $V_{\text{cell}} = 4/3^{3/2} \approx 0.7698\,V_P$
under the locked convention `HOP = "lP"`). Every node has a fixed processing
capacity $C = 100$ ticks/cycle (`max_node_ticks`) and every link a fixed
throughput: **one hop per tick**, so the local propagation speed is exactly
$v_{\text{hop}} = \ell_P/t_P = c$ — a strict round-trip throughput ceiling.

**A2 — Mass is workload.**
Physical mass-energy is not an added field; it is the *occupancy* of the network.
A system of energy $E$ holds the network to a workload $W$ in ticks via the
dictionary $E = W \cdot \kappa$ with the tick–energy constant $\kappa$
(`TICK_TO_MEV = 5.0 MeV/tick` — currently declared; see roadmap, D1). Congestion
$W(r)$ obeys the network's routing/queue dynamics; the Poisson-type relaxation
measured in `gr/` gives $W(r)/C = r_s/r$, and a node at saturation ($W \ge C$)
is a horizon. *Open: derive $\kappa$ from the axioms rather than declaring it
(the only fundamental scale of the theory, analogous to the lattice spacing fixed
by one measured scale in conventional lattice QCD — see D1).*

**A3 — The network is two-tier (client / server).**
- **Client space** is the observable lattice: matter, virtual carriers, waves,
  clocks, and all 118 elements are *client applications* — local routing
  processes on the A1 grid, constrained by the A2 capacity law and the A1
  throughput ceiling.
- **Server space** is a private state ledger: superposition, entanglement, and
  decoherence are *server-side functions*. A client particle carries **zero
  hidden metadata** (no angles, slit tags, partner coordinates); all
  multi-particle correlation state lives in server state-binding tables updated
  during `redraw()` ticks. The server never signals the client faster than the
  A1 ceiling (anti-FTL firewall; local marginals stay 50/50).

**A4 — Dynamics is tick-by-tick redraw.**
The universe advances in discrete ticks of $t_P$. Each tick: (i) client routing
steps along the 8 diagonal links at $\le c$; (ii) the server updates its state
tables by lazy evaluation (a particle in empty vacuum costs **zero** mid-flight
client updates — the emission ticket $(x_0,t_0)$ is only *evaluated* when its
forward causal cone contacts another particle's or detector's fringe — the
lazy two-cone handshake); (iii) congestion updates propagate on the queue
dynamics of A2. The `redraw()` rule is the dynamics of the theory; its full
formal statement (transition rules, conservation laws, measure on server
states) is the main outstanding item (see §4, F1).

**A5 — Born-rule commitment.**
When the lazy handshake commits a detection, the winning detector node is
selected with standard Born-rule weight $|\psi|^2$ (currently the one declared
statistical postulate; see §4, F3 for its derivation path).

---

## 2. Dictionary: physical concept ↔ network primitive

| Physics concept | Network primitive | Status |
| :--- | :--- | :--- |
| Light speed $c$ | link throughput: 1 diagonal hop / tick | **Axiom (A1)** |
| Planck units $\ell_P, t_P$ | lattice spacing / tick duration | **Axiom (A1)** |
| Mass–energy $E$ | node workload $W$ (ticks) via $E = W\kappa$ | Axiom (A2); $\kappa$ declared (D1) |
| Gravitational field | congestion distribution $W(r)$; $g_{00} = 1 - W/C$ | Measured (`gr/`); queue-delay derivation open (D2) |
| Black hole / horizon | saturated node $W \ge C$ (routing deadlock) | Measured (`gr/`, kugelblitz) |
| Superposition | un-evaluated server ticket (forward cone not yet intersected) | **Axiom (A3)** |
| Entanglement (Bell/GHZ) | shared server state-binding row; measured locally only at fringe contact | Measured (CHSH $|S|=2.85$, GHZ $M=4.0$) |
| Decoherence | `decohere()` at cone–fringe contact ("house of cards") | Measured (quantum eraser, $99.75\%$ lazy savings) |
| No-FTL signaling | server firewall: spacelike `decohere()` injects 50/50 noise | Measured (dense-coding firewall) |
| Matter / particles | client routing processes (quark walks, Steiner trees, zigzag clocks) | Measured (all 6 pillars) |
| Waves / light | Huygens client apps on the lattice (leapfrog front at $c$) | Measured (`huygens*`; speed knob open, D5) |
| Baryon asymmetry | non-planar chiral 3-hop twist density (192/512 = 3/8) on the 8-diagonal graph | **Derived** (Target A, zero-knob) |
| Confinement / glueball gap | SU(2) 4-link rhombus plaquette dynamics + 2×2 blocked operator | **Derived** (Targets B/D, zero-knob) |
| Light-quark bare ticks | chiral Dirac derivation on the BCC graph | **Derived** (Target C, zero-knob) |

---

## 3. Knob ledger: what is derived, declared, or derivable

`bcc_config.py` registers **39 declared knobs**. Target A, B, C, D already
*derive* their quantities from lattice geometry/gauge dynamics with zero fitted
inputs (they bypass the knobs entirely). The roadmap below assigns each
remaining knob class a derivation path. (Classification, not yet execution.)

| ID | Knob class (examples in `bcc_config.py`) | Derivation path | Priority |
| :--- | :--- | :--- | :--- |
| D1 | Energy dictionary: `TICK_TO_MEV = 5.0`, `link_weight_mev = 198` | Fix $\kappa$ by one measured scale — the BCC string tension from the Target F ensemble (the lattice-QCD analogue of fixing $a$ by $\sqrt{\sigma}$). Then every MeV number in `bcc/` and `elements/` converts from ticks without independent tuning. | **High** — largest single knob-class collapse |
| D2 | `W_to_g00_map` ($d\tau/dt = \sqrt{1-W/C}$), `lensing_queue` | **Done (Target H, `gr/bcc_congestion_queueing.py`, Nov 21).** The congestion profile is genuine (H1: local queue diffusion + point source, exact steady state $A(1/r-1/R)$ to 0.34%, $r_s = 3.69$ from $W=C$). The $\sqrt{1-W/C}$ map (declared OD2) reproduces the Schwarzschild time dilation within $1.47\%$ (H3); the standard M/M/1 queue map $1/(1-\rho)$ gives the Newtonian linear form and fails the bound (28% at $2r_s$) — so the $\sqrt{}$ map is the queue map *consistent with* GR, not a consequence of M/M/1 theory; its $\sim 1.5\%$ residual is the open-boundary term $\mathcal{O}(r_s/R)$. H4 (queue-potential integral): the two maps differ by exactly the derived factor 2 ($\Delta_A/\Delta_B = 2.012/2.005/2.002$ for $b = 16/24/32\, r_s$): M/M/1 has the GR effective-index depth ($n-1 \approx \rho \approx r_s/r$), the $\sqrt{}$ map the Newtonian half-depth. Open sub-question (sharpened F4): relating the two maps (temporal dilation vs. index/deflection depth) — the factor 2 that GR gets from $g_{ij}$ must come from the queue–geometry relation in the network. | **Closed as a derivation target; residual question merged into F4** |
| D3 | `QUARK_BARE_TICKS`, `baryon_bare_ticks`, `redraw_probs`, `meson_route_rule`, `meson_hyperfine` | Partially done by Target C (chiral Dirac gives light-quark bare ticks). Extend: derive all flavor bare ticks from chiral condensate structure on the BCC graph; derive routing rules from Steiner-tree optimality on the 8-diagonal graph. | Medium — large class, incremental |
| D4 | `huygens_dt = 0.55` (+ `huygens_*` set) | Derive the wave step from the lattice dispersion relation of the 8-diagonal hopping kernel: the continuum group velocity of the lowest mode must equal the A1 ceiling $c$; solve for the leapfrog parameter instead of declaring it. | Medium |
| D5 | `cmb_phase_shift = 0.2709`, `void_expand_thresh = 20.0`, `h_vac_rate` | Vacuum = queue below threshold: derive `void_expand_thresh` from the idle-queue noise of A2 (candidate: $C/\kappa$-relative scale — check the 100/5 relation). CMB phase shift from the D4 wave speed (cascade). | Medium |
| D6 | `baryo_step_factor_21`, `Omega_m0_Omega_L0`, `halo_profile`, `baryon_profile`, `hg_*` | Input data (Planck 2018, nuclear data) — legitimately declared *inputs*, not model knobs. Relabel as "data inputs" to shrink the honest knob count. | Low (paper hygiene) |

**Target metric:** reduce the honest declared-knob count from 39 toward the
single-scale core ($\kappa$ + A5 postulate) + relabeled data inputs.

---

## 4. Open theoretical questions (the honest list)

- **F1 — Formal dynamics.** The `redraw()` tick rule must be stated as an
  exact transition rule: client routing maps, server table update rule,
  congestion propagation, conservation laws (charge, energy/workload, baryon
  number). *This is what turns the framework from "a set of simulations" into
  a theory with a dynamics.*
- **F2 — 3D gauge sector vs 4D continuum.** (Updated Nov 25 with Targets I/J.)
  The BCC gauge dynamics is a **3D SU(2)** gauge theory (spatial lattice,
  spatial plaquettes). **BCC ratio:** $m_{0++}/\sqrt{\sigma} = 5.37/5.45/5.84/5.59$
  at $L = 8/12/16/20$ (Target F) and $5.682 \pm 0.182 / 5.964 \pm 0.191 /$
  $5.812 \pm 0.145$ at $L = 24/32/40$ (Target I, 5000-meas sweeps, verbatim F
  kernel) — L-stable up to $L = 40$ (all within $0.60 \times$ combined error of
  F's $L = 20$). The **3D continuum reference value on the BCC lattice is
  $5.81 \pm 0.15$** ($L = 40$), ~64% *above* the 4D continuum value
  $3.55 \pm 0.15$. The original "18% below" claim was an under-thermalization
  artifact (35 thermalization sweeps).
  **Target J (cubic refinement, Nov 25) overturned Target G's provisional
  verdict:** with the cubic bootstrap error shrunk 4.6x ($0.95 \to 0.206$ at
  $L = 40$), the cubic control gives $4.938 \pm 0.244 / 5.018 \pm 0.216 /$
  $5.118 \pm 0.206$ at $L = 24/32/40$; $\Delta$(cubic $-$ BCC) $= -0.74 /$
  $-0.95 / -0.69$, i.e. $2.4$–$3.3\sigma$ combined $\Rightarrow$ verdict
  **(ii) BCC-SPECIFIC**: the 8-diagonal BCC geometry lifts the ratio by ~15%
  relative to cubic. (Target G's $0.28\sigma$ $L = 20$ verdict was
  under-resolved — its cubic errors were 4–9x too large.)
  **Honest negatives (Target I):** (a) $\sqrt{\chi(2,2)}$ shows a small but
  resolvable L-drift ($0.6420 \to 0.6437$, $L = 24 \to 40$, beyond the
  $\sim 10^{-4}$ bootstrap errors) — the Wilson-loop tension is not strictly
  L-stable at $\beta = 2.15$; (b) the exploratory slope-fit "estimator sanity"
  criterion was miscalibrated at preregistration (Target F showed the same
  divergence pre-run: the global-vacuum-mean subtraction makes the slope fit
  not a valid $2\sigma$ cross-check); the genuine estimator consistency is the
  F$\leftrightarrow$I cross-run agreement, which holds.
  Open: *why* the 8-diagonal BCC geometry lifts the ratio (the BCC geometry is
  an A1 axiom, so this is a prediction the theory must derive — a lattice
  anisotropy of 3D gauge dynamics); a literature 3D reference value; and the
  gauge sector's relation to 4D physics (the network's "time" is the tick, not
  a lattice direction: this needs an argument, or the gauge sector must be
  extended to a 4th lattice dimension).
- **F3 — Born rule.** A5 is the remaining declared statistical postulate.
  Path: show $|\psi|^2$ commitment is the unique consistent assignment for
  lazy cone–fringe intersection (no-retrocausality + 50/50 marginals +
  frame-independent ordering constraints).
- **F4 — Spatial vs temporal correlators.** Target F/B measure the $0^{++}$
  decay along the embedding $z$ axis — a *spatial* correlation length, not an
  Euclidean-time one. In the rotationally invariant continuum limit the two
  coincide ($\xi = 1/m_{0++}$ in every direction); write the argument, and
  (optionally) verify with a second-direction correlator as a rotation check.
  *(Gravity counterpart, from Target H: the network's two queue maps give the
  two GR depth measures — M/M/1 $n-1 \approx \rho$ (the GR effective index, i.e.
  the full Einstein deflection in the asymptotic lens regime) and the declared
  $\sqrt{}$ map $n-1 \approx \rho/2$ (Newtonian half-depth, but the exact
  Schwarzschild time dilation). The factor 2 that GR attributes to the spatial
  metric $g_{ij}$ must be derived from the queue–geometry relation — the
  congestion→spatial-metric map — in the network. This is now a quantified
  open question, not a hand wave.)*
- **F5 — Continuum limit.** A scaling/renormalization statement for the
  BCC network: as the lattice is refined (or as one moves from the Planck
  scale to macroscopic scales), why do continuum physics and the client/server
  split emerge? The APE-smearing + blocked-operator machinery used in Target
  D is the prototype; the theory needs the general argument.

---

## 5. Falsifiability policy (unchanged discipline)

Every quantitative claim is preregistered in `PREREGISTRATION.md` *before*
execution, passed/failed against locked criteria in `run_all_benchmarks.py`,
with `bcc_config.py` SHA-256-audited on every run. New targets (D, E, ...)
must be added there first. Negative results are reported as negative results
(see Target F's preregistered decision fork). The theory is advanced by
*deriving* knobs away (D1–D6) and *preregistering* new out-of-sample
predictions — never by retuning.
