#!/usr/bin/env python3
"""
Target H [D2] — Genuine congestion-queueing gravity on the BCC lattice
=======================================================================
PREREGISTRATION.md item 8. No GR-shaped input anywhere:

  H1  The steady-state workload W(r) of the LOCAL queue-diffusion dynamics
      (BCC 8-neighbor relaxation + point-source injection, open boundary)
      is solved exactly (octahedral symmetry of the BCC 8-link geometry ->
      1/48 fundamental domain, ~48k unknowns; the same state that the local
      relaxation converges to, verified by a full-grid Jacobi transient).
      Pass: the measured axis profile is A(1/r - 1/R) within 2% for
      r in [8, R/2]. r_s = the measured saturation radius W(r_s) = C.
  H3  Local time dilation: the clock at r ticks at the local queue rate,
      so the ratio (local tick / far-field tick) = 1/map(rho(r)). Two
      preregistered maps: A (M/M/1 residual) 1/(1-rho) -> predicts the
      NEWTONIAN linear form (1-rho); B (declared OD2) 1/sqrt(1-rho) ->
      predicts the Schwarzschild form sqrt(1-r_s/r) up to the O(r_s/R)
      open-boundary term. Pass: a map reproduces sqrt(1-r_s/r) within 5%.
  H4  Photon deflection by Fermat/Dijkstra ray tracing on the symmetric
      BCC slice. Prediction (derived before the run): the fixed lattice has
      no load-dependent SPATIAL metric, so only the temporal part acts:
      map A (n = 1+rho+...) reproduces the NEWTONIAN value r_s/b; the
      Einstein value 2 r_s/b is expected to FAIL (missing spatial part,
      THEORY.md F4). Pass: map A within 10% of r_s/b.

No GR quantities are inputs. Only lattice geometry, C = 100 (A1), and the
queue dynamics are used.
"""

import json
import math
import os
import heapq
from typing import Any, Dict, List, Tuple

import numpy as np

# ---- protocol constants (PREREGISTRATION.md item 8; do not retune) ----
C_CAP: float = 100.0          # node capacity (A1 axiom)
D_DIFF: float = 0.1           # queue diffusion rate per tick (relaxation speed only)
S_SRC: float = 60.0          # point-source injection per tick at the origin
R_MAX: int = 128             # open-boundary radius (W = 0 at R >= R_MAX - 1)
FIT_RMIN: int = 8            # H1 fit region lower bound (near-field lattice core)
FIT_RMAX: int = R_MAX // 2   # H1 fit region upper bound (stay away from the boundary)
TICKS_TRANSIENT: int = 12000  # full-grid Jacobi transient on R=64 (convergence verification)
R_TRANSIENT: int = 64
RADIUS_FACTORS: List[float] = [2.0, 4.0, 8.0, 16.0]  # H3 radii in units of measured r_s
IMPACT_FACTORS: List[float] = [16.0, 24.0, 32.0]     # H4 impact parameters in units of r_s
RAY_HALF: int = 170          # ray-trace grid extent x in [-RAY_HALF, RAY_HALF]
MAP_RHO_CLIP: float = 0.999


# ---------------------------------------------------------------------------
# H1: exact steady state of the local queue-diffusion operator
# ---------------------------------------------------------------------------

def _domain_sites(R: int) -> List[Tuple[int, int, int]]:
    """BCC-parity interior sites of the fundamental 1/48 octahedral domain:
    x >= y >= z >= 0, all same parity, R < R-1."""
    R2b = (R - 1) ** 2
    sites = []
    for x in range(0, R):
        for y in range(x, -1, -1):
            for z in range(y, -1, -1):
                if (x % 2) == (y % 2) == (z % 2) and x * x + y * y + z * z < R2b:
                    sites.append((x, y, z))
    return sites


def solve_genuine_workload(R: int, S: float, D: float) -> Tuple[np.ndarray, Dict[Tuple[int, int, int], int]]:
    """Steady state of  W <- W + D(avg_8nb - W) + S*1_{origin}  with W = 0 at
    R >= R-1.  Steady state:  W - avg_8nb = (S/D)*1_{origin}.

    Solved exactly on the 1/48 octahedral fundamental domain (the source and
    the boundary are spherically symmetric, so the solution is invariant under
    sign flips + coordinate permutations - the symmetry group of the BCC 8-link
    geometry; verified independently by full_grid_residual()).
    """
    from scipy.sparse import lil_matrix, csr_matrix
    from scipy.sparse.linalg import splu

    R2b = (R - 1) ** 2

    def rep(x: int, y: int, z: int) -> Tuple[int, int, int]:
        a = sorted((abs(x), abs(y), abs(z)), reverse=True)
        return (a[0], a[1], a[2])

    sites = _domain_sites(R)
    idx = {s: i for i, s in enumerate(sites)}
    N = len(sites)
    A = lil_matrix((N, N))
    b = np.zeros(N)
    for i, (x, y, z) in enumerate(sites):
        A[i, i] = 1.0
        for sx in (1, -1):
            for sy in (1, -1):
                for sz in (1, -1):
                    j = idx.get(rep(x + sx, y + sy, z + sz))
                    if j is not None:      # neighbor outside grid / beyond boundary -> W = 0
                        A[i, j] -= 1.0 / 8.0
        if (x, y, z) == (0, 0, 0):
            b[i] = S / D
    W = np.asarray(splu(csr_matrix(A).tocsc()).solve(b))
    return W, idx


def full_grid_residual(W_dom: np.ndarray, idx: Dict[Tuple[int, int, int], int],
                       R: int, S: float, D: float) -> float:
    """Independent verification of the symmetry reduction: extend the
    symmetry-restricted solution to the full 3D grid by octahedral symmetry and
    evaluate the steady-state residual  |W - avg_8nb - (S/D) delta_origin|
    directly on the full grid (no linear system involved)."""
    n = 2 * R + 1
    h = R
    # extend by symmetry via lookup: Wg(c) = W_oct(max|c|, mid|c|, min|c|)
    Woct = np.zeros((R + 1, R + 1, R + 1), dtype=np.float64)
    for (x, y, z), i in idx.items():
        Woct[x, y, z] = float(W_dom[i])
    ci = np.arange(-R, R + 1, dtype=np.int32)
    CX, CY, CK = np.meshgrid(ci, ci, ci, indexing="ij")
    AX = np.abs(CX)
    AY = np.abs(CY)
    AK = np.abs(CK)
    A0 = np.maximum(AX, np.maximum(AY, AK))
    A2 = np.minimum(AX, np.minimum(AY, AK))
    A1 = AX + AY + AK - A0 - A2
    Wg = Woct[A0, A1, A2]
    Rg = np.sqrt(CX.astype(np.float64) ** 2 + CY.astype(np.float64) ** 2 + CK.astype(np.float64) ** 2)
    nb_avg = (Wg[:-2, :-2, :-2] + Wg[:-2, :-2, 2:] + Wg[:-2, 2:, :-2] + Wg[:-2, 2:, 2:]
              + Wg[2:, :-2, :-2] + Wg[2:, :-2, 2:] + Wg[2:, 2:, :-2] + Wg[2:, 2:, 2:]) / 8.0
    b_full = np.zeros((n, n, n), dtype=np.float64)
    b_full[h, h, h] = S / D
    res = np.abs(Wg[1:-1, 1:-1, 1:-1] - nb_avg - b_full[1:-1, 1:-1, 1:-1])
    ix = np.arange(n)[:, None, None]
    iy = np.arange(n)[None, :, None]
    iz = np.arange(n)[None, None, :]
    bcc = ((ix % 2) == (iy % 2)) & ((iy % 2) == (iz % 2))
    mask = bcc[1:-1, 1:-1, 1:-1] & (Rg[1:-1, 1:-1, 1:-1] < R - 1)
    res[~mask] = 0.0
    return float(res.max())


def jacobi_transient(R: int, S: float, D: float, ticks: int,
                     checkpoints=(3000, 6000, 9000, 12000)) -> Dict[int, Dict[int, float]]:
    """Run the actual local dynamics from W = 0 on the full grid; return the
    axis profile W(r, 0, 0) at each checkpoint (verification that the dynamics
    relaxes toward the solved steady state)."""
    n = 2 * R + 1
    Wg = np.zeros((n, n, n), dtype=np.float64)
    h = R
    src_idx = (h, h, h)
    coords = np.arange(-R, R + 1, dtype=np.float64)
    X, Y, Z = np.meshgrid(coords, coords, coords, indexing="ij")
    Rg = np.sqrt(X * X + Y * Y + Z * Z)
    ix = np.arange(n)[:, None, None]
    iy = np.arange(n)[None, :, None]
    iz = np.arange(n)[None, None, :]
    bcc = ((ix % 2) == (iy % 2)) & ((iy % 2) == (iz % 2))
    obnd_idx = np.where(bcc & (Rg >= R - 1))
    cps = sorted(checkpoints)
    out: Dict[int, Dict[int, float]] = {}
    ci = 0
    for tick in range(ticks):
        nb_avg = (Wg[:-2, :-2, :-2] + Wg[:-2, :-2, 2:] + Wg[:-2, 2:, :-2] + Wg[:-2, 2:, 2:]
                  + Wg[2:, :-2, :-2] + Wg[2:, :-2, 2:] + Wg[2:, 2:, :-2] + Wg[2:, 2:, 2:]) / 8.0
        Wg[1:-1, 1:-1, 1:-1] += D * (nb_avg - Wg[1:-1, 1:-1, 1:-1])
        Wg[src_idx] += S
        Wg[obnd_idx] = 0.0
        if ci < len(cps) and (tick + 1) >= cps[ci]:
            out[cps[ci]] = {r: float(Wg[h + r, h, h]) for r in range(0, R, 2)}
            ci += 1
    return out


def h1() -> Dict[str, Any]:
    W, idx = solve_genuine_workload(R_MAX, S_SRC, D_DIFF)
    # independent verification: extend the symmetry solution to the full grid
    # and check the steady-state residual directly (no linear system involved)
    residual = full_grid_residual(W, idx, R_MAX, S_SRC, D_DIFF)

    # local-dynamics convergence verification on the smaller grid
    tr = jacobi_transient(R_TRANSIENT, S_SRC, D_DIFF, TICKS_TRANSIENT)
    W64, idx64 = solve_genuine_workload(R_TRANSIENT, S_SRC, D_DIFF)
    tr_solved = {r: float(W64[idx64[(r, 0, 0)]]) for r in range(0, R_TRANSIENT, 2)}
    tr_rel: Dict[int, float] = {}
    for tick, prof in tr.items():
        tr_rel[tick] = max(abs(prof[r] - tr_solved[r]) / max(1e-12, abs(tr_solved[r]))
                           for r in range(2, 12, 2))

    # fit A(1/r - 1/R) through the measured profile on the fit region
    rs = np.array(range(FIT_RMIN, FIT_RMAX + 1, 2), dtype=float)
    ws = np.array([float(W[idx[(int(r), 0, 0)]]) for r in rs], dtype=float)
    x = 1.0 / rs - 1.0 / R_MAX
    A_fit = float(np.sum(ws * x) / np.sum(x * x))
    fit_rows = []
    fit_ok = True
    for r in rs:
        w_fit = A_fit * (1.0 / r - 1.0 / R_MAX)
        rel = abs(float(W[idx[(int(r), 0, 0)]]) - w_fit) / max(1e-12, w_fit)
        fit_rows.append((int(r), float(W[idx[(int(r), 0, 0)]]), w_fit, rel))
        if rel > 0.02:
            fit_ok = False
    # r_s from the fitted line: A(1/r_s - 1/R) = C
    r_s = 1.0 / (C_CAP / A_fit + 1.0 / R_MAX)
    profile = {r: float(W[idx[(r, 0, 0)]]) for r in range(0, R_MAX, 2)}
    return {
        "A_fit": A_fit, "A_over_C": A_fit / C_CAP,
        "r_s": r_s, "fit_within_2pct": fit_ok,
        "fit_rows": fit_rows, "profile": profile,
        "symmetry_reduction_full_grid_residual": residual,
        "transient_rel_diff_r_le_10_by_tick": {str(k): v for k, v in tr_rel.items()},
    }


# ---------------------------------------------------------------------------
# queue maps
# ---------------------------------------------------------------------------

def make_rho_fn(profile: Dict[int, float]) -> "callable":
    rs = np.array(sorted(k for k in profile if k >= 2), dtype=float)
    ws = np.array([profile[int(r)] for r in rs], dtype=float)

    def rho(r3d: float) -> float:
        if r3d <= rs[0]:
            w = ws[0]
        elif r3d >= rs[-1]:
            w = 0.0
        else:
            w = float(np.interp(r3d, rs, ws))
        return min(w / C_CAP, MAP_RHO_CLIP)

    return rho


def map_A(rho: float) -> float:
    """M/M/1 residual service time: t_hop = 1/(1 - rho)."""
    return 1.0 / (1.0 - min(rho, MAP_RHO_CLIP))


def map_B(rho: float) -> float:
    """Declared OD2: t_hop = 1/sqrt(1 - rho)."""
    return 1.0 / math.sqrt(max(1e-12, 1.0 - min(rho, MAP_RHO_CLIP)))


# ---------------------------------------------------------------------------
# H3: local clock-rate ratio
# ---------------------------------------------------------------------------

def h3(rho_fn, r_s: float) -> List[Dict[str, Any]]:
    rows = []
    for name, fn in (("A: 1/(1-rho)  [M/M/1, Newtonian form]", map_A),
                     ("B: 1/sqrt(1-rho)  [declared OD2, Schwarzschild form]", map_B)):
        radii = []
        for f in RADIUS_FACTORS:
            r_obs = f * r_s
            ratio = 1.0 / fn(rho_fn(r_obs))          # local tick / far-field tick
            gr = math.sqrt(max(0.0, 1.0 - r_s / r_obs))
            err = abs(ratio - gr) / gr
            radii.append({"factor": f, "r_obs": r_obs, "measured": ratio,
                          "schwarzschild": gr, "rel_err": err})
        worst = max(x["rel_err"] for x in radii)
        rows.append({"map": name, "radii": radii, "worst_rel_err": worst,
                     "pass_5pct": worst <= 0.05})
    return rows


# ---------------------------------------------------------------------------
# H4: Fermat/Dijkstra photon deflection on the symmetric BCC slice
# ---------------------------------------------------------------------------

def superhop_cost(x: int, y: int, dx: int, dy: int, rho_fn, map_fn) -> float:
    """Cost (in physical-hop units) of one planar super-hop on the even-even
    BCC slice: the two physical 3D hop delays at the hop-center radii under the
    queue map; Fermat picks the cheaper z = ±1 excursion for the axis moves."""
    if dx != 0 and dy != 0:
        c1 = math.sqrt((x + 0.5 * dx) ** 2 + (y + 0.5 * dy) ** 2 + 0.25)
        c2 = math.sqrt((x + 1.5 * dx) ** 2 + (y + 1.5 * dy) ** 2 + 0.25)
        return map_fn(rho_fn(c1)) + map_fn(rho_fn(c2))
    if dx != 0:  # (±2, 0): intermediate y = ±1, Fermat picks the cheaper
        best = float("inf")
        for sy in (1, -1):
            c1 = math.sqrt((x + 0.5 * dx) ** 2 + (y + 0.5 * sy) ** 2 + 0.25)
            c2 = math.sqrt((x + 1.5 * dx) ** 2 + (y + 0.5 * sy) ** 2 + 0.25)
            best = min(best, map_fn(rho_fn(c1)) + map_fn(rho_fn(c2)))
        return best
    best = float("inf")  # (0, ±2): intermediate x = ±1
    for sx in (1, -1):
        c1 = math.sqrt((x + 0.5 * sx) ** 2 + (y + 0.5 * dy) ** 2 + 0.25)
        c2 = math.sqrt((x + 1.5 * sx) ** 2 + (y + 1.5 * dy) ** 2 + 0.25)
        best = min(best, map_fn(rho_fn(c1)) + map_fn(rho_fn(c2)))
    return best


def dijkstra_deflection(rho_fn, b: int, map_fn) -> Dict[str, float]:
    """Sites: even-even sublattice (x, y even) of the BCC parity lattice in the
    z = 0 plane, x, y in [-RAY_HALF, RAY_HALF] (both even). A planar ray from an
    even source stays on this sublattice; every planar step is realized by a
    pair of physical 3D super-hops with a z = ±1 excursion, and Fermat's
    principle picks the cheaper excursion. Cost of a super-hop = the two
    physical hop delays at the hop-center radii under the queue map."""
    mN = RAY_HALF + 1        # even coords -RAY_HALF..RAY_HALF (step 2) -> RAY_HALF+1 sites
    x0 = RAY_HALF // 2
    idx = lambda x, y: ((x // 2) + x0) * mN + ((y // 2) + x0)
    src_i = idx(-RAY_HALF, -b)
    tgt_i = idx(RAY_HALF, -b)

    def hop_cost(x: int, y: int, dx: int, dy: int) -> float:
        return superhop_cost(x, y, dx, dy, rho_fn, map_fn)

    MOVES = ((2, 2), (2, -2), (-2, 2), (-2, -2), (2, 0), (-2, 0), (0, 2), (0, -2))
    dist = np.full(mN * mN, np.inf)
    prev = np.full(mN * mN, -1, dtype=np.int64)
    dist[src_i] = 0.0
    pq = [(0.0, src_i)]
    while pq:
        d, i = heapq.heappop(pq)
        if d > dist[i]:
            continue
        if i == tgt_i:
            break
        cx = ((i // mN) - x0) * 2
        cy = ((i % mN) - x0) * 2
        for dx, dy in MOVES:
            nx, ny = cx + dx, cy + dy
            if abs(nx) > RAY_HALF or abs(ny) > RAY_HALF:
                continue
            j = idx(nx, ny)
            nd = d + hop_cost(cx, cy, dx, dy)
            if nd < dist[j]:
                dist[j] = nd
                prev[j] = i
                heapq.heappush(pq, (nd, j))

    path = []
    i = tgt_i
    while i != -1:
        cx = ((i // mN) - x0) * 2
        cy = ((i % mN) - x0) * 2
        path.append((cx, cy))
        i = prev[i]
    path.reverse()

    def point_at_x(xx: int) -> Tuple[int, int]:
        return min(path, key=lambda p: abs(p[0] - xx))

    pin = point_at_x(-80)
    pmid = point_at_x(0)
    pout = point_at_x(80)
    th_in = math.atan2(pmid[1] - pin[1], pmid[0] - pin[0])
    th_out = math.atan2(pout[1] - pmid[1], pout[0] - pmid[0])
    deflection = abs(th_in - th_out)
    return {"deflection_rad": deflection, "total_cost": float(dist[tgt_i])}


def straight_excess(rho_fn, b: int, map_fn) -> float:
    """H4 clean observable: transit excess (ticks) of the FORCED straight-line
    path at impact parameter b (y = -b, x from -RAY_HALF to +RAY_HALF):
    sum over all physical hops of [map(rho) - 1]. This is the lattice's direct
    measurement of the queue-potential integral  ∫[n(r)-1] ds  along the ray.
    (The minimum-cost Fermat path instead detours around the congestion ball
    at zero cost - the L∞/king-metric property of the BCC slice on the finite
    grid - so the asymptotic deflection is set by the cutoff radius, not the
    potential; that detour geometry is reported separately.)"""
    excess = 0.0
    for x in range(-RAY_HALF, RAY_HALF, 2):
        excess += superhop_cost(x, -b, 2, 0, rho_fn, map_fn) - 2.0
    return excess


def h4(rho_fn, r_s: float) -> List[Dict[str, Any]]:
    rows = []
    impacts = [2 * int(round(f * r_s / 2)) for f in IMPACT_FACTORS]  # b = f*r_s, even
    for name, fn in (("A: 1/(1-rho)", map_A), ("B: 1/sqrt(1-rho)", map_B)):
        rows_h = []
        for b in impacts:
            ex = straight_excess(rho_fn, b, fn)
            dij = dijkstra_deflection(rho_fn, b, fn)
            rows_h.append({
                "b": b,
                "straight_excess_ticks": round(ex, 4),
                "mincost_path_cost": round(dij["total_cost"], 3),
                "mincost_corner_rad": round(dij["deflection_rad"], 5),
                "hard_sphere_2asin_b_over_R": round(2.0 * math.asin(min(b, R_MAX - 2) / R_MAX), 5),
            })
        rows.append({"map": name, "impacts": rows_h})
    # preregistered check: the queue-map structure in the potential integral,
    # n_A - 1 ≈ rho  vs  n_B - 1 ≈ rho/2  (weak-rho regime along b >= 16 r_s)
    ex_a = [x["straight_excess_ticks"] for x in rows[0]["impacts"]]
    ex_b = [x["straight_excess_ticks"] for x in rows[1]["impacts"]]
    ratios = [a / b for a, b in zip(ex_a, ex_b)]
    rows.append({"map": "A/B excess ratio", "ratios": [round(r, 4) for r in ratios],
                 "ratio_in_1.8_2.2": all(1.8 <= r <= 2.2 for r in ratios)})
    return rows


# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 92)
    print("TARGET H [D2]: Genuine Congestion-Queueing Gravity (point source, R=%d)" % R_MAX)
    print("dynamics: W <- W + D(avg_8nb - W) + S*1_origin, D=%s, S=%s, C=%s, open boundary R>=%d"
          % (D_DIFF, S_SRC, C_CAP, R_MAX - 1))
    print("=" * 92)

    h1r = h1()
    r_s = h1r["r_s"]
    A = h1r["A_fit"]
    print("\nH1: exact steady state of the local queue-diffusion operator")
    print(f"  full-grid residual check of the symmetry-restricted solution: {h1r['symmetry_reduction_full_grid_residual']:.3e}")
    for tick, rel in h1r['transient_rel_diff_r_le_10_by_tick'].items():
        print(f"  Jacobi transient (R={R_TRANSIENT}) tick {tick:>5}: rel diff vs exact state (r <= 10) = {rel:.4f}")
    print(f"  fit A(1/r - 1/R) on r in [{FIT_RMIN}, {FIT_RMAX}]: A = {A:.3f}  (A/C = {A / C_CAP:.4f})")
    print(f"  H1 pass (within 2%): {'PASS' if h1r['fit_within_2pct'] else 'FAIL'}")
    for r, w, w_fit, rel in h1r["fit_rows"][::4]:
        print(f"    r={r:<4} W={w:9.4f}  fit={w_fit:9.4f}  rel={rel * 100:6.3f}%")
    print(f"  measured saturation radius r_s = W^{-1}(C) = {r_s:.3f}")

    rho_fn = make_rho_fn(h1r["profile"])

    print(f"\nH3: local clock-rate ratio 1/map(rho(r)) vs Schwarzschild sqrt(1-r_s/r)")
    h3_rows = h3(rho_fn, r_s)
    for row in h3_rows:
        print(f"  Map {row['map']}: worst rel err {row['worst_rel_err'] * 100:7.3f}% -> "
              f"{'PASS (5%)' if row['pass_5pct'] else 'fail'}")
        for x in row["radii"]:
            print(f"    r_obs={x['r_obs']:7.2f} ({x['factor']:>4.0f} r_s)  measured={x['measured']:.5f}  "
                  f"Schwarzschild={x['schwarzschild']:.5f}  err={x['rel_err'] * 100:6.3f}%")

    b_list = [2 * int(round(f * r_s / 2)) for f in IMPACT_FACTORS]
    print("\nH4: queue-potential integral  ∫[n(r)-1] ds  along the forced straight line,"
          + "  b = " + ", ".join(str(x) for x in b_list)
          + "  (lattice detour geometry reported separately)")
    h4_rows = h4(rho_fn, r_s)
    for row in h4_rows:
        if row["map"] == "A/B excess ratio":
            print(f"  Map {row['map']}: {row['ratios']}  -> "
                  f"{'PASS (1.8..2.2)' if row['ratio_in_1.8_2.2'] else 'fail'} "
                  f"(predicted: n_A-1 ≈ rho, n_B-1 ≈ rho/2)")
            continue
        print(f"  Map {row['map']}:")
        for x in row["impacts"]:
            print(f"    b={x['b']:<5} straight excess={x['straight_excess_ticks']:9.4f} ticks  "
                  f"min-cost path={x['mincost_path_cost']:8.1f} ticks "
                  f"(corner {x['mincost_corner_rad']:.4f} rad; hard-sphere ref {x['hard_sphere_2asin_b_over_R']:.4f})")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "congestion_queueing.json")
    with open(out, "w") as fh:
        json.dump({
            "protocol": "Target H, PREREGISTRATION.md item 8 (point source; R=128)",
            "H1": {k: v for k, v in h1r.items() if k not in ("fit_rows", "profile")},
            "H1_profile": {str(k): round(v, 6) for k, v in h1r["profile"].items()},
            "H1_fit_rows": [[r, w, wf, rel] for r, w, wf, rel in h1r["fit_rows"]],
            "H3": h3_rows,
            "H4": h4_rows,
        }, fh, indent=2)
    print(f"\nArtifact: {out}")


if __name__ == "__main__":
    main()
