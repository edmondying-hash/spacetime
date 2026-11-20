#!/usr/bin/env python3
"""
Lazy Two-Cone Pascal Handshake & Fringe-Contact Decoherence (`serverside/lazy_pascal_handshake.py`).

Implements lazy server-side quantum evaluation on the 3D BCC lattice:
  1. Zero Mid-Flight Client Updates: Unmeasured particles exist only as lightweight
     emission tickets (x0, t0) on the server, burning 0 vacuum node ticks in flight.
  2. Fringe-Contact Decoherence ("House of Cards"): Whenever a particle's expanding
     Pascal cone fringe touches a thermal gas molecule or detector fringe, the server
     automatically triggers `decohere()`.
  3. Inverted Backward Pascal Cone Intersection: At `decohere()`, the server intersects
     the forward cone from (x0, t0) with the inverted backward cone from (x_det, t_det),
     summing zigzag turn phases (+1 vs +i) just-in-time to yield |psi|^2 interference.
"""

import cmath
import math
import random
from typing import Any, Dict, List, Optional, Tuple


class LazyQuantumTicket:
    """Zero-workload client handle; actual path history stays unrendered until fringe contact."""

    def __init__(self, label: str, emit_tick: int, slits: Tuple[int, ...]):
        self.label = label
        self.emit_tick = emit_tick
        self.slits = slits
        self.collapsed = False
        self.collapse_tick: Optional[int] = None
        self.collapse_reason: str = "Unmeasured (Superposition)"
        self.realized_y: Optional[int] = None


class LazyPascalServer:
    """Server-side just-in-time two-cone Pascal evaluator with fringe-contact decoherence."""

    def __init__(self, seed: int = 2026):
        self.rng = random.Random(seed)
        self.server_ops = 0
        self.client_node_updates = 0

    def emit_superposition(self, label: str, emit_tick: int, slits: Tuple[int, ...]) -> LazyQuantumTicket:
        """Register an unrendered superposition ticket on the server (0 client node updates)."""
        self.server_ops += 1
        return LazyQuantumTicket(label=label, emit_tick=emit_tick, slits=slits)

    def _zigzag_amplitude_two_cone(
        self, y_start: int, y_end: int, delta_t: int
    ) -> Tuple[complex, int]:
        """
        Intersect the forward Pascal cone from (y_start, 0) with the inverted backward
        cone from (y_end, delta_t). Only paths inside the overlapping diamond contribute!
        """
        dy = y_end - y_start
        if abs(dy) > delta_t or ((delta_t - abs(dy)) % 2 != 0):
            return 0j, 0

        # Number of +1 (up-right) and -1 (down-right) diagonal steps inside the two-cone diamond
        n_up = (delta_t + dy) // 2
        n_dn = (delta_t - dy) // 2

        # Exact DP over the intersecting diamond tracking last step direction (+1 or -1)
        # Turn phase: straight step = +1, 90-degree zigzag turn = +i
        dp_up: Dict[Tuple[int, int], complex] = {}
        dp_dn: Dict[Tuple[int, int], complex] = {}

        if n_up > 0:
            dp_up[(1, 0)] = 1.0 + 0j
        if n_dn > 0:
            dp_dn[(0, 1)] = 1.0 + 0j

        for u in range(n_up + 1):
            for d in range(n_dn + 1):
                if u + d <= 1:
                    continue
                amp_u = 0j
                if u > 0:
                    # Continue straight up (+1) or turn from down (+i)
                    amp_u += dp_up.get((u - 1, d), 0j) * 1.0
                    amp_u += dp_dn.get((u - 1, d), 0j) * 1j
                    dp_up[(u, d)] = amp_u
                amp_d = 0j
                if d > 0:
                    # Continue straight down (+1) or turn from up (+i)
                    amp_d += dp_dn.get((u, d - 1), 0j) * 1.0
                    amp_d += dp_up.get((u, d - 1), 0j) * 1j
                    dp_dn[(u, d)] = amp_d

        total_amp = dp_up.get((n_up, n_dn), 0j) + dp_dn.get((n_up, n_dn), 0j)
        diamond_cells = (n_up + 1) * (n_dn + 1)
        # Normalize by Pascal binomial weight 2^(delta_t / 2)
        norm = 2.0 ** (0.5 * delta_t)
        return total_amp / norm, diamond_cells
    def decohere_on_fringe_contact(
        self,
        ticket: LazyQuantumTicket,
        contact_tick: int,
        screen_half_width: int = 16,
        which_path_tagged: bool = False,
    ) -> Dict[str, Any]:
        """
        Triggered the exact tick a client's outer Pascal fringe touches another particle
        or detector screen. Runs the inverted backward cone handshake and commits 1 outcome.
        """
        if ticket.collapsed:
            return {"already_collapsed": True, "realized_y": ticket.realized_y}

        delta_t = max(1, contact_tick - ticket.emit_tick)
        y_positions = list(range(-screen_half_width, screen_half_width + 1))
        weights: List[float] = []
        total_diamond_cells = 0

        for y_det in y_positions:
            if which_path_tagged:
                # Slit fringe already touched an air molecule/sensor -> incoherent sum |A_L|^2 + |A_R|^2
                prob = 0.0
                for s_y in ticket.slits:
                    amp, cells = self._zigzag_amplitude_two_cone(s_y, y_det, delta_t)
                    prob += abs(amp) ** 2
                    total_diamond_cells += cells
            else:
                # Unperturbed vacuum flight -> coherent two-cone amplitude sum |A_L + A_R|^2
                amp_sum = 0j
                for s_y in ticket.slits:
                    amp, cells = self._zigzag_amplitude_two_cone(s_y, y_det, delta_t)
                    amp_sum += amp
                    total_diamond_cells += cells
                prob = abs(amp_sum) ** 2
            weights.append(prob)

        w_sum = sum(weights)
        if w_sum <= 0.0:
            chosen_y = 0
        else:
            r = self.rng.random() * w_sum
            cum = 0.0
            chosen_y = y_positions[-1]
            for y_val, w in zip(y_positions, weights):
                cum += w
                if r <= cum:
                    chosen_y = y_val
                    break

        ticket.collapsed = True
        ticket.collapse_tick = contact_tick
        ticket.realized_y = chosen_y
        ticket.collapse_reason = (
            "Mid-flight air fringe contact (fringes washed out)"
            if which_path_tagged
            else "Detector screen fringe contact (coherent two-cone handshake)"
        )
        # Only the realized transaction updates 1 client detector node
        self.client_node_updates += 1
        self.server_ops += total_diamond_cells

        return {
            "delta_t": delta_t,
            "realized_y": chosen_y,
            "weights": dict(zip(y_positions, weights)),
            "lazy_diamond_ops": total_diamond_cells,
        }


def run_lazy_handshake_demo() -> None:
    print("=" * 92)
    print("PART 1: Eager Full-Grid Wave Update vs. Lazy Two-Cone Pascal Handshake (Bandwidth Audit)")
    print("=" * 92)
    print("Flight Ticks (dT)   Eager 3D Grid Updates   Lazy Mid-Flight   Lazy Handshake   Savings")
    print("-" * 92)

    srv = LazyPascalServer(seed=42)
    for dt in (10, 20, 40, 80):
        # Eager simulation updates ~ (2*t + 1)^3 BCC nodes at every tick t = 1..dt
        eager_updates = sum((2 * t + 1) ** 3 for t in range(1, dt + 1))
        tkt = srv.emit_superposition(f"photon_{dt}", emit_tick=0, slits=(-4, 4))
        res = srv.decohere_on_fringe_contact(tkt, contact_tick=dt, screen_half_width=16, which_path_tagged=False)
        lazy_total = res["lazy_diamond_ops"]
        savings_pct = (1.0 - (lazy_total / eager_updates)) * 100.0
        print(
            f"{dt:>17} {eager_updates:>23,} {0:>17} {lazy_total:>16,} {savings_pct:>9.3f}%"
        )

    print("\n" + "=" * 92)
    print("PART 2: Fringe-Contact Decoherence ('House of Cards') — Vacuum vs. 300 K Air Collision")
    print("=" * 92)
    print("Screen Y   Coherent Vacuum (No Fringe Touch)   300 K Air Contact (Slit Fringe Touched)")
    print("-" * 92)

    srv_coh = LazyPascalServer(seed=101)
    tkt_vac = srv_coh.emit_superposition("vac_photon", emit_tick=0, slits=(-4, 4))
    res_vac = srv_coh.decohere_on_fringe_contact(tkt_vac, contact_tick=24, screen_half_width=12, which_path_tagged=False)

    srv_air = LazyPascalServer(seed=101)
    tkt_air = srv_air.emit_superposition("air_photon", emit_tick=0, slits=(-4, 4))
    res_air = srv_air.decohere_on_fringe_contact(tkt_air, contact_tick=24, screen_half_width=12, which_path_tagged=True)

    for y in range(-12, 13, 2):
        p_vac = res_vac["weights"].get(y, 0.0)
        p_air = res_air["weights"].get(y, 0.0)
        bar_v = "#" * int(p_vac * 45)
        bar_a = "*" * int(p_air * 45)
        print(f"{y:>8}   {p_vac:>8.4f} {bar_v:<24}   {p_air:>8.4f} {bar_a}")


if __name__ == "__main__":
    run_lazy_handshake_demo()

