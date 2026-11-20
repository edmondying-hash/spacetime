#!/usr/bin/env python3
"""
3D BCC Dual-Channel (+/-) Pascal Walk vs. Continuous 3D Wave-Equation |psi|^2
(`bcc/bcc_dual_pascal_born.py`).

Upgrades the 1D integer (+/-) Pascal walk onto the full 8-diagonal 3D BCC lattice:
  1. Pure integer tick counting across two phase channels (N_+ and N_-) along all
     8 BCC body diagonals (dx, dy, dz) in {-1, +1}^3.
  2. Exact 3D destructive cancellation (N_+ - N_- = 0) carving dark nodal planes
     across x, y, and z simultaneously.
  3. Born-rule detection workload (N_+ - N_-)^2 converging directly to the continuous
     3D wave-equation probability density |psi(x, y, z)|^2 as ticks N grow.
"""

import itertools
import math
from typing import Any, Dict, List, Tuple

BCC_DIAGONALS: List[Tuple[int, int, int]] = list(itertools.product((-1, 1), repeat=3))


def compute_3d_bcc_pascal_distribution(n_ticks: int = 12) -> Dict[str, Any]:
    """Run n_ticks of 8-diagonal 3D BCC integer (+/-) hops and compare to continuous 3D |psi|^2."""
    state: Dict[Tuple[int, int, int], Tuple[int, int]] = {(0, 0, 0): (1, 0)}

    for tick in range(1, n_ticks + 1):
        next_state: Dict[Tuple[int, int, int], Tuple[int, int]] = {}
        even_tick = (tick % 2 == 0)

        for (x, y, z), (pos, neg) in state.items():
            for dx, dy, dz in BCC_DIAGONALS:
                # On even ticks, each +1 axis projection applies a pi-phase channel swap
                flips = ((1 if dx == 1 else 0) + (1 if dy == 1 else 0) + (1 if dz == 1 else 0)) if even_tick else 0
                add_pos, add_neg = (neg, pos) if (flips % 2 == 1) else (pos, neg)

                coord = (x + dx, y + dy, z + dz)
                cur_pos, cur_neg = next_state.get(coord, (0, 0))
                next_state[coord] = (cur_pos + add_pos, cur_neg + add_neg)

        state = next_state

    coords = sorted(state.keys())
    classical_total = sum(pos + neg for pos, neg in state.values()) or 1
    born_total = sum((pos - neg) ** 2 for pos, neg in state.values()) or 1

    raw_wave = {
        (x, y, z): (
            math.exp(-(x * x + y * y + z * z) / float(n_ticks))
            * (math.cos(math.pi * x / 4.0) ** 2)
            * (math.cos(math.pi * y / 4.0) ** 2)
            * (math.cos(math.pi * z / 4.0) ** 2)
        )
        for (x, y, z) in coords
    }
    wave_total = sum(raw_wave.values()) or 1.0

    # Collect full 3D error metrics and extract the central slice (y=0, z=0) for display
    max_diff_3d = 0.0
    central_slice_rows: List[Dict[str, Any]] = []

    for coord in coords:
        pos, neg = state[coord]
        net_psi = pos - neg
        p_class = (pos + neg) / classical_total
        p_born = (net_psi ** 2) / born_total
        p_wave = raw_wave[coord] / wave_total
        diff = p_born - p_wave
        if abs(diff) > max_diff_3d:
            max_diff_3d = abs(diff)

        x, y, z = coord
        if y == 0 and z == 0:
            central_slice_rows.append({
                "x": x,
                "pos": pos,
                "neg": neg,
                "net_psi": net_psi,
                "p_classical": p_class,
                "p_born": p_born,
                "p_wave": p_wave,
                "diff": diff,
            })

    return {
        "n_ticks": n_ticks,
        "active_3d_nodes": len(coords),
        "slice_rows": central_slice_rows,
        "max_abs_diff_3d": max_diff_3d,
    }


def run_3d_bcc_pascal_demo() -> None:
    res12 = compute_3d_bcc_pascal_distribution(n_ticks=12)

    print("=== PART 1: 3D BCC 8-Diagonal (+/-) Walk Central Slice (y=0, z=0, N=12 Ticks) ===")
    header = (
        f"{'Pos x':>6} {'N_+':>10} {'N_-':>10} {'Net psi':>10} {'Classical':>10} "
        f"{'Born (dN)^2':>11} {'WaveEq |psi|^2':>14} {'Diff':>8}  Pattern"
    )
    print(header)
    print("-" * len(header))

    # Normalize slice bars relative to slice max so pattern shape is crystal clear
    max_slice_p = max((r["p_born"] for r in res12["slice_rows"]), default=1.0) or 1.0
    for r in res12["slice_rows"]:
        bar = "#" * int(round((r["p_born"] / max_slice_p) * 28))
        tag = " <-- 3D Dark Node" if r["net_psi"] == 0 else ""
        print(
            f"{r['x']:6d} {r['pos']:10d} {r['neg']:10d} {r['net_psi']:10d} {r['p_classical']:10.5f} "
            f"{r['p_born']:11.5f} {r['p_wave']:14.5f} {r['diff']:+8.5f}  {bar}{tag}"
        )

    print("\n=== PART 2: 3D BCC Convergence Toward Continuous 3D Wave Equation as Ticks Increase ===")
    print(f"{'Ticks (N)':>10} {'Active 3D Nodes':>17} {'Max 3D |Born - WaveEq| Error':>30}")
    print("-" * 60)
    for n in (12, 24, 36, 48):
        summary = compute_3d_bcc_pascal_distribution(n_ticks=n)
        print(f"{n:10d} {summary['active_3d_nodes']:17,d} {summary['max_abs_diff_3d']:30.7f}")


if __name__ == "__main__":
    run_3d_bcc_pascal_demo()
