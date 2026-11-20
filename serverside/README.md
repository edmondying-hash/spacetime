# Non-Local Server State Bus, Lazy Evaluation & Firewall (`serverside/`)

This directory implements the **Server Space** tier of the **3D BCC Spacetime Network**—holding private kernel state-binding tables carried invisibly during `redraw()` ticks while keeping `ClientParticle` handles strictly zero-metadata.

---

## Core Server-Side Quantum Mechanisms

1. **Lazy Two-Cone Pascal Handshake & Fringe-Contact Decoherence (`lazy_pascal_handshake.py`):**
   - **Zero Mid-Flight Client Updates:** Unmeasured particles remain lightweight emission tickets $(x_0, t_0)$ on the server, burning **0 vacuum node ticks** during flight (`>99.9%` bandwidth savings over eager wave updates).
   - **Fringe-Contact Trigger ("House of Cards"):** Whenever a particle's expanding Pascal cone fringe touches a thermal gas molecule or detector fringe, the server triggers `decohere()`—intersecting the forward emission cone with an inverted backward detector cone to evaluate $|\psi|^2$ just-in-time.
2. **Bell & GHZ Non-Locality (`entangled_bell_server.py`, `spacetime_server_api.py`):**
   - Resolves spacelike-separated 2-particle Bell tests (**$|S| = 2.8544 > 2.0$**) and 3-particle GHZ Mermin tests (**$M = 4.0000$**) with exact `50/50` local marginals and thermal vacuum-noise decoherence curves.
3. **Delayed-Choice Quantum Eraser (`quantum_eraser_server.py`):**
   - Post-sorts signal detections against idler polarization bases (`|+>` vs. `|->`) to recover complementary interference fringes and anti-fringes without retrocausal client signaling.
4. **Anti-FTL No-Signaling Firewall & Superdense Coding (`dense_coding_firewall.py`):**
   - Enforces relativistic causality by injecting random outcomes on `decohere()` and one-time-pad scrambling in transit—blocking FTL signaling (`0.4939` noise) while enabling `100.0%` 4-state superdense decoding at $v \le c$.
5. **Octant-Symmetry Huygens Wavefront Solver (`octant_huygens_fast.py`):**
   - Exploits 8-fold cubic/BCC octant symmetry to accelerate spherical wavefront convergence, driving continuum anisotropy error down from `0.840%` ($R=30$) to **`0.056%`** ($R=240$).

---

## Directory Structure & Quick Start (`serverside/`)

| File | Description | Run Command |
| :--- | :--- | :--- |
| `lazy_pascal_handshake.py` | Lazy two-cone (forward + inverted backward) Pascal handshake & fringe-contact decoherence (`>99.9%` bandwidth savings). | `python3 lazy_pascal_handshake.py` |
| `entangled_bell_server.py` | Spacelike-separated Bell CHSH benchmark ($|S| > 2.0$, exact `50/50` marginals). | `python3 entangled_bell_server.py` |
| `spacetime_server_api.py` | Zero-metadata `ClientParticle` + 4-primitive kernel API (`entangle`, `redraw`, `decohere`, `read`) with Bell & GHZ sweeps. | `python3 spacetime_server_api.py` |
| `quantum_eraser_server.py` | Delayed-choice quantum eraser sorting complementary fringe and anti-fringe patterns. | `python3 quantum_eraser_server.py` |
| `dense_coding_firewall.py` | Anti-FTL signaling firewall, transit scrambling & `100.0%` 4-state superdense coding. | `python3 dense_coding_firewall.py` |
| `octant_huygens_fast.py` | $8\times$ octant-symmetry continuum isotropy benchmark ($R = 60 \dots 240 \to 0.056\%$ error). | `python3 octant_huygens_fast.py` |
