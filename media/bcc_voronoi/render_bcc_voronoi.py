#!/usr/bin/env python3
"""Render the 70 s BCC Voronoi-cell explainer (1920x1080 @ 30 fps).

Volume label is read from bcc_config.DERIVED under the locked default HOP='lP'
and shown as 0.770 V_P (three decimals). The geometric fact '4 coord³ = half
the conventional cube' is separate and is not called a prediction.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/workspace/bcc_test4_videos/v2_sound/_common")
import bccvid as bv  # noqa: E402  (loudnorm_mux, audio_report, extras helpers)

# Locked-default config (no BCC_HOP override) from the recorded source tree.
os.environ.pop("BCC_HOP", None)
TREE = "/workspace/spacetime_upload/v7/ed_extract/spacetime"
for p in (TREE, os.path.join(TREE, "bcc")):
    if p not in sys.path:
        sys.path.insert(0, p)
import importlib
import bcc_config as cfg
importlib.reload(cfg)
from plot_bcc_3d_cell import build_truncated_octahedron_faces  # noqa: E402

assert cfg.HOP == "lP", cfg.HOP
VOL_VP = float(cfg.DERIVED["cell_volume_VP"])
HOP = str(cfg.HOP)
VOL_3 = f"{VOL_VP:.3f}"   # 0.770
VOL_4 = f"{VOL_VP:.4f}"   # 0.7698
COORD_UNIT = float(cfg.DERIVED["coord_unit_lP"])

W, H, DPI, FPS = 1920, 1080, 100, 30
BG, PANEL, GRID = "#0b0d13", "#121622", "#2a3142"
FG, DIM = "#e8ebf2", "#8b94a8"
CYAN, ORANGE, RED = "#4fd1ff", "#ffb347", "#ff5c6c"
GREEN, VIOLET = "#6ee7a0", "#b39dff"
CELL_HEX, CELL_SQ, CELL_EDGE = "#2ec4d6", "#ffb347", "#d7f6ff"
OCT_FILL, CENTER, NN_COL, SEC_COL = "#8b7cff", "#e63946", "#4fd1ff", "#ffb347"
ELEV0, AZIM0 = 22, 38
TITLE = "BCC Voronoi Cell"
FOOTER = "Geometry is standard BCC  ·  V_P / HOP labels use the model's OD1 units"
WATERMARK = "/workspace/watermark/b_dark.png"

# Scene timings (70 s total)
BEATS = [
    ("neighbours", 10.0, "1  /  6   ·   Neighbours",
     "One BCC node and its 8 body-diagonal neighbours"),
    ("octahedron", 12.0, "2  /  6   ·   Octahedron",
     "The 8 nearest-neighbour bisectors cut a regular octahedron"),
    ("truncation", 12.0, "3  /  6   ·   Truncation",
     "Second-neighbour planes cut the corners — 8 hexagons + 6 squares"),
    ("volume", 10.0, "4  /  6   ·   Volume",
     "Volume is half the conventional cube  ·  the V_P label is a unit choice"),
    ("tessellation", 20.0, "5  /  6   ·   Tessellation",
     "Neighbouring cells tile space without gaps"),
    ("end", 6.0, "6  /  6   ·   End card", None),
]
STARTS = []
_t = 0.0
for _n, _d, _h, _c in BEATS:
    STARTS.append(_t)
    _t += _d
TOTAL = _t
assert abs(TOTAL - 70.0) < 1e-9, TOTAL

# Animation cue times, local to each beat (also written to timeline.json)
NN_T0, NN_DT, NN_FADE = 0.40, 0.65, 0.30          # beat 1, all eight in by ~5.0 s
PL_T0, PL_DT, PL_FADE = 0.35, 0.80, 0.55          # beat 2 planes
OCT_LOCK_LOCAL = PL_T0 + 7 * PL_DT + 0.6          # after last plane
SEC_T0, SEC_DT, SEC_FADE = 0.20, 0.22, 0.25       # beat 3 second neighbours
CUT_T0, CUT_DT, CUT_FADE = 1.20, 0.55, 0.40       # beat 3 cutting planes
CELL3_T0, CELL3_FADE = 3.60, 1.80                 # truncated cell fade-in
LEGEND3_T0, LEGEND3_FADE = 6.40, 0.80
POP_DUR, POP_FADE = 6.0, 0.35                     # beat 5
ORBIT_T0 = 6.0

plt.rcParams.update({
    "font.family": "DejaVu Sans", "text.color": FG, "axes.labelcolor": FG,
    "xtick.color": DIM, "ytick.color": DIM, "axes.edgecolor": GRID,
    "axes.facecolor": PANEL, "figure.facecolor": BG, "savefig.facecolor": BG,
    "font.size": 16,
})


def ease(x):
    x = max(0.0, min(1.0, float(x)))
    return x * x * (3 - 2 * x)


def ramp(t, t0, dur=0.5):
    if dur <= 0:
        return float(t >= t0)
    return ease((t - t0) / dur)


def fade_io(t, T, cin=0.35, cout=0.30):
    return min(ramp(t, 0.0, cin), 1.0 - ramp(t, T - cout, cout))


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


CORNERS = list(itertools.product((-1.0, 1.0), repeat=3))
# A readable reveal order around the cell (not hidden first)
NN_ORDER = [
    (1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1),
    (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1),
]
SECOND = [(2.0, 0, 0), (-2.0, 0, 0), (0, 2.0, 0), (0, -2.0, 0), (0, 0, 2.0), (0, 0, -2.0)]


def shift_faces(faces, offset):
    o = np.asarray(offset, dtype=float)
    return [np.asarray(f, dtype=float) + o for f in faces]


def octahedron_faces(r=1.5):
    return [
        np.array([(sx * r, 0, 0), (0, sy * r, 0), (0, 0, sz * r)])
        for sx, sy, sz in itertools.product((-1.0, 1.0), repeat=3)
    ]


def plane_polygon(center, normal, radius, n=28):
    nrm = np.asarray(normal, dtype=float)
    nrm = nrm / np.linalg.norm(nrm)
    ref = np.array([1.0, 0.0, 0.0]) if abs(nrm[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(nrm, ref); u /= np.linalg.norm(u)
    v = np.cross(nrm, u)
    c = np.asarray(center, dtype=float)
    angs = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.array([c + radius * (math.cos(a) * u + math.sin(a) * v) for a in angs])


def axis_square(axis, val, half=1.15):
    pts = []
    for a, b in [(-half, -half), (half, -half), (half, half), (-half, half)]:
        p = [0.0, 0.0, 0.0]
        p[axis] = val
        p[(axis + 1) % 3] = a
        p[(axis + 2) % 3] = b
        pts.append(p)
    return np.array(pts)


def tessellation_sites():
    sites = []
    for x, y, z in itertools.product((0, 1, 2, 3), repeat=3):
        if (x % 2) == (y % 2) == (z % 2):
            sites.append((x - 1.5, y - 1.5, z - 1.5))
    sites.sort(key=lambda p: (p[0] ** 2 + p[1] ** 2 + p[2] ** 2, p[0], p[1], p[2]))
    assert len(sites) == 16
    return sites


def draw_cube_wire(ax, low=-1.0, high=1.0, color="#b7bec9", lw=1.2, alpha=0.7, ls="--"):
    pts = list(itertools.product((low, high), repeat=3))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if sum(1 for a, b in zip(pts[i], pts[j]) if a != b) == 1:
                xs, ys, zs = zip(pts[i], pts[j])
                ax.plot(xs, ys, zs, linestyle=ls, linewidth=lw, color=color, alpha=alpha)


def draw_triad(ax, scale=0.55, lw=2.0, alpha=1.0):
    ax.plot([0, scale], [0, 0], [0, 0], color=RED, lw=lw, alpha=alpha, zorder=20)
    ax.plot([0, 0], [0, scale], [0, 0], color=GREEN, lw=lw, alpha=alpha, zorder=20)
    ax.plot([0, 0], [0, 0], [0, scale], color=CYAN, lw=lw, alpha=alpha, zorder=20)


def style_3d(ax, lim=1.45, elev=ELEV0, azim=AZIM0, ticks=None):
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_facecolor(BG)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((0, 0, 0, 0))
        axis.pane.set_edgecolor((*_hex(GRID), 0.55))
        axis.pane.set_alpha(0.0)
        try:
            axis._axinfo["grid"]["color"] = (0.16, 0.19, 0.26, 0.35)
            axis._axinfo["grid"]["linewidth"] = 0.4
        except Exception:
            pass
    ax.tick_params(colors=DIM, labelsize=11, pad=2)
    if ticks is None:
        ticks = [-1, 0, 1]
    ax.set_xticks(ticks); ax.set_yticks(ticks); ax.set_zticks(ticks)
    ax.set_xlabel("X", color=RED, labelpad=6, fontsize=12)
    ax.set_ylabel("Y", color=GREEN, labelpad=6, fontsize=12)
    ax.set_zlabel("Z", color=CYAN, labelpad=6, fontsize=12)
    ax.xaxis.line.set_color(RED)
    ax.yaxis.line.set_color(GREEN)
    ax.zaxis.line.set_color(CYAN)


def add_poly(ax, faces, fc, ec, alpha, lw=1.15, zsort="average"):
    if alpha <= 0.002:
        return None
    poly = Poly3DCollection(
        [np.asarray(f) for f in faces],
        facecolors=fc, edgecolors=ec, linewidths=lw, alpha=float(min(1.0, alpha)),
    )
    try:
        poly.set_zsort(zsort)
    except Exception:
        pass
    ax.add_collection3d(poly)
    return poly


# Precomputed geometry
FACES = build_truncated_octahedron_faces()  # 6 squares + 8 hexes
SQUARES, HEXES = FACES[:6], FACES[6:]
OCT_FACES = octahedron_faces(1.5)
SITES = tessellation_sites()
SITE_PARITY = [
    int(round((o[0] + 1.5) + (o[1] + 1.5) + (o[2] + 1.5))) % 2 for o in SITES
]
NN_PLANE_POLYS = [
    plane_polygon(np.array(c) * 0.5, c, radius=1.05, n=32) for c in NN_ORDER
]
CUT_PLANES = [axis_square(axis, val, half=1.15) for axis in range(3) for val in (-1.0, 1.0)]
OCT_TIPS = np.array([
    [1.5, 0, 0], [-1.5, 0, 0], [0, 1.5, 0], [0, -1.5, 0], [0, 0, 1.5], [0, 0, -1.5]
])


# ---------------------------------------------------------------------------
# Beat 5 tessellation: pyvista offscreen with depth peeling.
# Matplotlib's 3D transparency sort turned muddy mid-orbit; this is the fallback
# named in the brief. Do not call reset_camera_clipping_range() — it makes the
# transparent cells vanish under depth peeling.
# ---------------------------------------------------------------------------
class TessPV:
    FILL = ("#2ec4d6", "#6b8cff")
    OPAC = 0.38
    R = 13.0

    def __init__(self):
        self.pl = None
        self.cell_actors = []
        self.node_actors = []

    def _cam(self, elev, azim):
        er, ar = math.radians(elev), math.radians(azim)
        return (
            self.R * math.cos(er) * math.cos(ar),
            self.R * math.cos(er) * math.sin(ar),
            self.R * math.sin(er),
        )

    @staticmethod
    def _poly(faces, offset):
        o = np.asarray(offset, dtype=float)
        verts, index, faces_idx = [], {}, []
        for f in faces:
            ids = []
            for v in np.asarray(f, dtype=float) + o:
                key = tuple(np.round(v, 10))
                if key not in index:
                    index[key] = len(verts)
                    verts.append(key)
                ids.append(index[key])
            faces_idx.append(ids)
        cells = np.hstack([[len(f), *f] for f in faces_idx])
        import pyvista as pv
        return pv.PolyData(np.array(verts, dtype=float), cells)

    def start(self):
        if self.pl is not None:
            return
        import pyvista as pv
        pl = pv.Plotter(off_screen=True, window_size=(W, H))
        pl.set_background(BG)
        pl.enable_depth_peeling(number_of_peels=24, occlusion_ratio=0.0)
        try:
            pl.enable_anti_aliasing("ssaa")
        except Exception:
            pass
        self.cell_actors, self.node_actors = [], []
        for i, off in enumerate(SITES):
            ca = pl.add_mesh(
                self._poly(FACES, off), color=self.FILL[SITE_PARITY[i]],
                opacity=self.OPAC, smooth_shading=False, show_edges=True,
                edge_color=CELL_EDGE, line_width=1.6, lighting=True,
                specular=0.15, diffuse=0.9, ambient=0.4,
            )
            na = pl.add_mesh(pv.Sphere(radius=0.055, center=off), color=FG, lighting=False)
            self.cell_actors.append(ca)
            self.node_actors.append(na)
        pl.add_mesh(pv.Line((0, 0, 0), (1.4, 0, 0)), color=RED, line_width=3)
        pl.add_mesh(pv.Line((0, 0, 0), (0, 1.4, 0)), color=GREEN, line_width=3)
        pl.add_mesh(pv.Line((0, 0, 0), (0, 0, 1.4)), color=CYAN, line_width=3)
        for pt, lab, col in (
            ((1.7, 0, 0), "X", RED),
            ((0, 1.7, 0), "Y", GREEN),
            ((0, 0, 1.7), "Z", CYAN),
        ):
            pl.add_point_labels(
                np.array([pt]), [lab], text_color=col, font_size=22,
                shape=None, always_visible=True, fill_shape=False, show_points=False,
            )
        self.pl = pl

    def shot(self, elev, azim, alphas):
        self.start()
        pl = self.pl
        for i, a in enumerate(alphas):
            vis = a > 0.01
            self.cell_actors[i].SetVisibility(vis)
            self.node_actors[i].SetVisibility(vis)
            if vis:
                self.cell_actors[i].GetProperty().SetOpacity(self.OPAC * float(a))
                self.node_actors[i].GetProperty().SetOpacity(float(a))
        pl.camera_position = [self._cam(elev, azim), (0, 0, 0), (0, 0, 1)]
        pl.render()
        return np.asarray(pl.screenshot(return_img=True))

    def close(self):
        if self.pl is not None:
            self.pl.close()
            self.pl = None


TESS = TessPV()


# Watermark buffer (96 px, lower right)
_wm = Image.open(WATERMARK).convert("RGBA").resize((96, 96), Image.Resampling.LANCZOS)
WM = np.array(_wm)
WM_A = (WM[:, :, 3:4].astype(np.float32) / 255.0) * 0.92
WM_RGB = WM[:, :, :3].astype(np.float32)
WM_X, WM_Y = W - 96 - 36, H - 96 - 48


def stamp_wm(buf):
    """Composite the channel mark onto an HxWx4 uint8 frame (in place)."""
    roi = buf[WM_Y:WM_Y + 96, WM_X:WM_X + 96, :3]
    roi[:] = (roi.astype(np.float32) * (1.0 - WM_A) + WM_RGB * WM_A + 0.5).astype(np.uint8)
    buf[WM_Y:WM_Y + 96, WM_X:WM_X + 96, 3] = 255
    return buf


def chrome(fig, heading, caption, cap_alpha=1.0, footer=FOOTER):
    fig.text(0.032, 0.955, TITLE, fontsize=22, color=DIM, weight="bold", va="center")
    fig.text(0.97, 0.955, heading, fontsize=20, color=FG, ha="right", va="center")
    if caption and cap_alpha > 0.02:
        fig.text(
            0.50, 0.078, caption,
            fontsize=26, color=FG, ha="center", va="center", alpha=cap_alpha,
            bbox=dict(boxstyle="round,pad=0.45", fc="#000000", ec="none", alpha=0.55 * cap_alpha),
        )
    fig.text(0.50, 0.018, footer, fontsize=13, color=DIM, ha="center", va="center")


# ---------------------------------------------------------------------------
# Per-beat drawing. Each returns a cache key of the visual state.
# ---------------------------------------------------------------------------

def draw_neighbours(fig, t, T):
    ax = fig.add_axes([0.07, 0.12, 0.86, 0.78], projection="3d")
    style_3d(ax, lim=1.45)
    draw_cube_wire(ax, -1, 1)
    draw_triad(ax)
    alphas = [ramp(t, NN_T0 + i * NN_DT, NN_FADE) for i in range(8)]
    for i, (cx, cy, cz) in enumerate(NN_ORDER):
        a = alphas[i]
        if a <= 0:
            continue
        ax.plot([0, cx], [0, cy], [0, cz], color="#1d6ea8", lw=2.3, alpha=0.95 * a)
        ax.scatter([cx], [cy], [cz], s=110, color=NN_COL, edgecolors="white",
                   linewidths=0.6, depthshade=False, zorder=12, alpha=a)
    ax.scatter([0], [0], [0], s=220, color=CENTER, edgecolors="white",
               linewidths=0.8, depthshade=False, zorder=15)
    la = ramp(t, 0.05, 0.4)
    ax.text2D(0.02, 0.90, "Center node  (0, 0, 0)", transform=ax.transAxes,
              color=CENTER, fontsize=15, weight="bold", alpha=la)
    ax.text2D(0.02, 0.84, "8 nearest neighbours  (±1, ±1, ±1)", transform=ax.transAxes,
              color=NN_COL, fontsize=15, alpha=ramp(t, NN_T0, 0.4))
    ax.text2D(0.02, 0.78, "body-diagonal distance  =  √3", transform=ax.transAxes,
              color=DIM, fontsize=14, alpha=ramp(t, NN_T0 + 0.4, 0.4))
    n_on = sum(1 for a in alphas if a > 0.99)
    return ("n", n_on, int(la * 20), int(ramp(t, NN_T0, 0.4) * 20))


def draw_octahedron(fig, t, T):
    ax = fig.add_axes([0.07, 0.12, 0.86, 0.78], projection="3d")
    style_3d(ax, lim=1.75, ticks=[-1.5, -1, 0, 1, 1.5])
    draw_cube_wire(ax, -1, 1, alpha=0.25)
    draw_triad(ax, scale=0.45)
    palphas = [ramp(t, PL_T0 + i * PL_DT, PL_FADE) for i in range(8)]
    for i, (cx, cy, cz) in enumerate(NN_ORDER):
        ax.plot([0, cx], [0, cy], [0, cz], color=CENTER, lw=1.4, alpha=0.55)
        a = palphas[i]
        if a > 0:
            add_poly(ax, [NN_PLANE_POLYS[i]], fc="#4fd1ff", ec="#8be3ff", alpha=0.10 * a, lw=0.8)
        ax.scatter([cx], [cy], [cz], s=70, color=NN_COL, edgecolors="white",
                   linewidths=0.4, depthshade=False, zorder=12)
    oct_a = ramp(t, OCT_LOCK_LOCAL - 1.2, 1.2)
    if oct_a > 0:
        add_poly(ax, OCT_FACES, fc=OCT_FILL, ec="#e4dcff", alpha=0.28 * oct_a, lw=1.3)
        ax.scatter(OCT_TIPS[:, 0], OCT_TIPS[:, 1], OCT_TIPS[:, 2], s=40, color=VIOLET,
                   edgecolors="white", linewidths=0.4, depthshade=False, zorder=12, alpha=oct_a)
    ax.scatter([0], [0], [0], s=160, color=CENTER, edgecolors="white", linewidths=0.7,
               depthshade=False, zorder=15)
    ax.text2D(0.02, 0.90, "8 perpendicular bisector planes", transform=ax.transAxes,
              color=CYAN, fontsize=15, weight="bold", alpha=ramp(t, 0.1, 0.4))
    ax.text2D(0.02, 0.84, "intersection  =  regular octahedron", transform=ax.transAxes,
              color=VIOLET, fontsize=15, alpha=ramp(t, OCT_LOCK_LOCAL - 0.6, 0.5))
    ax.text2D(0.02, 0.78, "vertices at  (±1.5, 0, 0)  and cyclic", transform=ax.transAxes,
              color=DIM, fontsize=14, alpha=ramp(t, OCT_LOCK_LOCAL, 0.5))
    n_on = sum(1 for a in palphas if a > 0.99)
    return ("o", n_on, int(oct_a * 20))


def draw_truncation(fig, t, T):
    ax = fig.add_axes([0.28, 0.12, 0.68, 0.78], projection="3d")
    style_3d(ax, lim=2.15, ticks=[-2, -1, 0, 1, 2])
    draw_cube_wire(ax, -1, 1, alpha=0.3)
    draw_triad(ax, scale=0.45)
    oct_a = 0.22 * (1.0 - ramp(t, CELL3_T0, CELL3_FADE))
    if oct_a > 0.02:
        add_poly(ax, OCT_FACES, fc=OCT_FILL, ec="#c9c0ff", alpha=oct_a, lw=0.6)
    calphas = [ramp(t, CUT_T0 + i * CUT_DT, CUT_FADE) for i in range(6)]
    for i, a in enumerate(calphas):
        if a > 0:
            add_poly(ax, [CUT_PLANES[i]], fc=ORANGE, ec="#ffd08a", alpha=0.10 * a, lw=0.8)
    cell_a = ramp(t, CELL3_T0, CELL3_FADE)
    if cell_a > 0:
        add_poly(ax, HEXES, fc=CELL_HEX, ec=CELL_EDGE, alpha=0.32 * cell_a, lw=1.25)
        add_poly(ax, SQUARES, fc=CELL_SQ, ec="#ffe0a8", alpha=0.45 * cell_a, lw=1.35)
    salphas = [ramp(t, SEC_T0 + i * SEC_DT, SEC_FADE) for i in range(6)]
    for i, p in enumerate(SECOND):
        a = salphas[i]
        if a <= 0:
            continue
        ax.plot([0, p[0]], [0, p[1]], [0, p[2]], color=SEC_COL, lw=1.1, alpha=0.55 * a)
        ax.scatter([p[0]], [p[1]], [p[2]], s=80, color=SEC_COL, edgecolors="white",
                   linewidths=0.5, depthshade=False, zorder=12, alpha=a)
    c = np.array(CORNERS)
    ax.scatter(c[:, 0], c[:, 1], c[:, 2], s=45, color=NN_COL, edgecolors="white",
               linewidths=0.3, depthshade=False, alpha=0.7, zorder=11)
    ax.scatter([0], [0], [0], s=170, color=CENTER, edgecolors="white", linewidths=0.7,
               depthshade=False, zorder=15)
    ax.text2D(0.02, 0.92, "6 second neighbours  (±2, 0, 0)  cyclic", transform=ax.transAxes,
              color=ORANGE, fontsize=15, weight="bold", alpha=ramp(t, 0.05, 0.4))
    ax.text2D(0.02, 0.86, "bisector planes  |x|, |y|, |z|  =  1", transform=ax.transAxes,
              color=ORANGE, fontsize=14, alpha=ramp(t, CUT_T0, 0.4))
    ax.text2D(0.02, 0.80, "truncate the 6 octahedron tips", transform=ax.transAxes,
              color=DIM, fontsize=14, alpha=ramp(t, CUT_T0 + 0.6, 0.4))
    la = ramp(t, LEGEND3_T0, LEGEND3_FADE)
    if la > 0.02:
        fig.patches.append(
            FancyBboxPatch(
                (0.028, 0.175), 0.30, 0.28,
                boxstyle="round,pad=0.012,rounding_size=0.012",
                facecolor="#121622", edgecolor="#2a3142", linewidth=1.2,
                transform=fig.transFigure, zorder=0, alpha=la,
            )
        )
        fig.text(0.045, 0.415, "8  hexagons", color=CELL_HEX, fontsize=20, weight="bold",
                 va="center", alpha=la)
        fig.text(0.045, 0.375, "toward  (±1, ±1, ±1)", color=DIM, fontsize=15, va="center", alpha=la)
        fig.text(0.045, 0.315, "6  squares", color=ORANGE, fontsize=20, weight="bold",
                 va="center", alpha=la)
        fig.text(0.045, 0.275, "toward  (±2, 0, 0)", color=DIM, fontsize=15, va="center", alpha=la)
        fig.text(0.045, 0.215, "14  faces", color=FG, fontsize=20, weight="bold", va="center", alpha=la)
        fig.text(0.045, 0.178, "truncated octahedron", color=DIM, fontsize=15, va="center", alpha=la)
    n_s = sum(1 for a in salphas if a > 0.99)
    n_c = sum(1 for a in calphas if a > 0.99)
    return ("t", n_s, n_c, int(cell_a * 20), int(la * 20))


def draw_volume(fig, t, T):
    ax = fig.add_axes([0.03, 0.12, 0.54, 0.78], projection="3d")
    style_3d(ax, lim=1.45)
    draw_cube_wire(ax, -1, 1, color="#c5ccd6", lw=1.3, alpha=0.7, ls="--")
    draw_triad(ax, scale=0.4)
    add_poly(ax, HEXES, fc=CELL_HEX, ec=CELL_EDGE, alpha=0.33, lw=1.2)
    add_poly(ax, SQUARES, fc=CELL_SQ, ec="#ffe0a8", alpha=0.48, lw=1.3)
    ax.scatter([0], [0], [0], s=170, color=CENTER, edgecolors="white", linewidths=0.7,
               depthshade=False, zorder=15)
    ax.text2D(0.04, 0.90, "Conventional cube  side 2,  volume 8", transform=ax.transAxes,
              color=DIM, fontsize=13)

    def line(y, text, color=FG, size=22, weight="normal", a=1.0):
        if a > 0.02:
            fig.text(0.58, y, text, fontsize=size, color=color, va="center", weight=weight, alpha=a)

    a1 = ramp(t, 0.15, 0.55)
    a2 = ramp(t, 0.70, 0.55)
    a3 = ramp(t, 1.50, 0.55)
    a4 = ramp(t, 2.30, 0.55)
    a5 = ramp(t, 3.40, 0.80)
    line(0.82, "Volume of the cell", FG, 26, "bold", a1)
    line(0.74, "4  coord³", CYAN, 48, "bold", a2)
    line(0.66, "=  half of the conventional cube  (side 2  →  volume 8)", DIM, 16, "normal", a3)
    line(0.58, "measured volume  =  4.000", DIM, 16, "normal", a4)
    if a5 > 0.02:
        fig.patches.append(
            FancyBboxPatch(
                (0.575, 0.20), 0.39, 0.30,
                boxstyle="round,pad=0.012,rounding_size=0.012",
                facecolor="#121622", edgecolor="#2a3142", linewidth=1.2,
                transform=fig.transFigure, zorder=0, alpha=a5,
            )
        )
        line(0.46, f"Node cell  =  {VOL_3} V_P", FG, 24, "bold", a5)
        line(0.40, f"HOP  =  {HOP}", CYAN, 20, "bold", a5)
        line(0.345, "Model unit convention  ·  not a prediction", ORANGE, 15, "bold", a5)
        line(0.29, "1 coord  =  l_P/√3    ·    V_P  =  l_P³", DIM, 15, "normal", a5)
        line(0.24, f"4 / (3√3)  =  {VOL_4}, shown as  {VOL_3}", DIM, 14, "normal", a5)
    return ("v", int(a1 * 10), int(a2 * 10), int(a3 * 10), int(a4 * 10), int(a5 * 20))


def _cam_dir(elev, azim):
    er, ar = math.radians(elev), math.radians(azim)
    return np.array([math.cos(er) * math.cos(ar), math.cos(er) * math.sin(ar), math.sin(er)])


def tess_camera(t):
    if t <= ORBIT_T0:
        return 18.0, 52.0
    u = (t - ORBIT_T0) / (20.0 - ORBIT_T0)
    azim = 52.0 + 70.0 * u
    elev = 18.0 + 4.0 * math.sin(math.pi * u)
    return elev, azim


def cell_alpha(t, i):
    # Stagger 16 cells over POP_DUR, each fading in over POP_FADE
    t0 = (i + 0.15) * (POP_DUR - POP_FADE) / 16.0
    return ramp(t, t0, POP_FADE)


def draw_tessellation(fig, t, T):
    elev, azim = tess_camera(t)
    alphas = [cell_alpha(t, i) for i in range(16)]
    img = TESS.shot(elev, azim, alphas)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, origin="upper", interpolation="nearest")
    ax.set_axis_off()
    ax.set_xlim(-0.5, W - 0.5)
    ax.set_ylim(H - 0.5, -0.5)
    la1 = ramp(t, 0.05, 0.4)
    la2 = ramp(t, 1.0, 0.5)
    fig.text(0.05, 0.88, "16 BCC sites   ·   2 × 2 × 2 conventional cells",
             color=FG, fontsize=15, weight="bold", alpha=la1)
    fig.text(0.05, 0.835, "truncated octahedra fill space with no gaps",
             color=CYAN, fontsize=15, alpha=la2)
    n_on = sum(1 for a in alphas if a > 0.99)
    return ("s", n_on, round(elev, 2), round(azim, 2))


def draw_end(fig, t, T):
    a0 = ramp(t, 0.05, 0.45)
    fig.text(0.50, 0.82, "What this shows", fontsize=40, weight="bold",
             ha="center", va="center", color=FG, alpha=a0)
    lines = [
        (0.68, 0.40, "The Voronoi cell of a BCC node is a truncated octahedron.", FG),
        (0.60, 0.70, "8 hexagonal faces toward the nearest neighbours  (±1, ±1, ±1).", CYAN),
        (0.52, 1.00, "6 square faces toward the second neighbours  (±2, 0, 0).", ORANGE),
        (0.44, 1.30, "Volume  =  4 coord³  =  half the conventional cube of side 2.", GREEN),
        (0.36, 1.60, "The cells tile space with no gaps.", FG),
        (0.26, 2.00, f"Node cell  =  {VOL_3} V_P  under the model's OD1 convention  (HOP = {HOP}).", DIM),
        (0.20, 2.40, "That label is a unit choice, not a prediction.", ORANGE),
    ]
    keys = [int(a0 * 10)]
    for y, t0, text, col in lines:
        a = ramp(t, t0, 0.45)
        if a > 0.02:
            fig.text(0.50, y, text, fontsize=23, color=col, ha="center", va="center", alpha=a)
        keys.append(int(a * 10))
    return ("e", *keys)


DRAW = {
    "neighbours": draw_neighbours,
    "octahedron": draw_octahedron,
    "truncation": draw_truncation,
    "volume": draw_volume,
    "tessellation": draw_tessellation,
    "end": draw_end,
}


def render_frame(fig, beat_idx, t_local):
    name, dur, heading, caption = BEATS[beat_idx]
    fig.clear()
    fig.set_facecolor(BG)
    key = DRAW[name](fig, t_local, dur)
    cap_a = fade_io(t_local, dur) if caption else 0.0
    chrome(fig, heading, caption, cap_a)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba()).copy()
    if buf.shape[0] != H or buf.shape[1] != W:
        # unexpected DPI rounding; fall back to a resize
        im = Image.fromarray(buf).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
        buf = np.array(im)
    stamp_wm(buf)
    # cache key includes caption fade quantized so holds still work
    return buf, (beat_idx, key, int(cap_a * 20))


def scene_for_time(t):
    acc = 0.0
    for i, (_, dur, _, _) in enumerate(BEATS):
        if t < acc + dur or i == len(BEATS) - 1:
            return i, t - acc
        acc += dur
    return len(BEATS) - 1, 0.0


PREVIEW_TIMES = [
    0.4, 1.2, 2.5, 6.0,
    10.4, 13.0, 16.5, 20.5,
    22.5, 25.5, 29.0, 32.5,
    34.5, 37.0, 40.0, 43.0,
    44.4, 47.0, 49.5, 54.0, 58.0, 62.5,
    64.2, 67.5,
]


def write_png(buf, path):
    Image.fromarray(buf[:, :, :3]).save(path, "PNG", optimize=True)


def preview(out_dir):
    prev = os.path.join(out_dir, "preview")
    os.makedirs(prev, exist_ok=True)
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)
    paths = []
    for t in PREVIEW_TIMES:
        i, tl = scene_for_time(t)
        buf, _ = render_frame(fig, i, tl)
        p = os.path.join(prev, f"t{t:05.1f}s.png")
        write_png(buf, p)
        paths.append(p)
        print(f"preview {t:5.1f}s -> {p}")
    TESS.close()
    plt.close(fig)
    return paths


def cheap_key(beat_idx, t):
    """Quantized visual state so fully held frames are not redrawn."""
    name, dur, _, cap = BEATS[beat_idx]
    cap_q = int(fade_io(t, dur) * 20) if cap else 0
    if name == "neighbours":
        return ("n", tuple(int(ramp(t, NN_T0 + i * NN_DT, NN_FADE) * 20) for i in range(8)),
                int(ramp(t, 0.05, 0.4) * 20), int(ramp(t, NN_T0, 0.4) * 20), cap_q)
    if name == "octahedron":
        return ("o", tuple(int(ramp(t, PL_T0 + i * PL_DT, PL_FADE) * 20) for i in range(8)),
                int(ramp(t, OCT_LOCK_LOCAL - 1.2, 1.2) * 20),
                int(ramp(t, OCT_LOCK_LOCAL - 0.6, 0.5) * 20),
                int(ramp(t, OCT_LOCK_LOCAL, 0.5) * 20), cap_q)
    if name == "truncation":
        return ("t", tuple(int(ramp(t, SEC_T0 + i * SEC_DT, SEC_FADE) * 20) for i in range(6)),
                tuple(int(ramp(t, CUT_T0 + i * CUT_DT, CUT_FADE) * 20) for i in range(6)),
                int(ramp(t, CELL3_T0, CELL3_FADE) * 20),
                int(ramp(t, LEGEND3_T0, LEGEND3_FADE) * 20), cap_q)
    if name == "volume":
        return ("v", tuple(int(ramp(t, t0, d) * 20) for t0, d in
                           ((0.15, 0.55), (0.70, 0.55), (1.50, 0.55), (2.30, 0.55), (3.40, 0.80))), cap_q)
    if name == "tessellation":
        elev, azim = tess_camera(t)
        return ("s", tuple(int(cell_alpha(t, i) * 20) for i in range(16)),
                round(elev, 2), round(azim, 2), cap_q)
    if name == "end":
        times = [0.05, 0.40, 0.70, 1.00, 1.30, 1.60, 2.00, 2.40]
        return ("e", tuple(int(ramp(t, t0, 0.45) * 10) for t0 in times), cap_q)
    return (name, round(t, 3), cap_q)


def render_silent(out_dir, mp4_path, crf=18):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    last_key = None
    last_bytes = None
    t0 = time.time()
    rendered = 0
    try:
        for f in range(n):
            t = f / FPS
            i, tl = scene_for_time(min(t, TOTAL - 1e-9))
            key = cheap_key(i, tl)
            if key == last_key and last_bytes is not None:
                proc.stdin.write(last_bytes)
            else:
                buf, _ = render_frame(fig, i, tl)
                last_bytes = buf.tobytes()
                last_key = key
                proc.stdin.write(last_bytes)
                rendered += 1
            if f % 60 == 0 or f == n - 1:
                elapsed = time.time() - t0
                rate = (f + 1) / max(elapsed, 1e-6)
                eta = (n - f - 1) / max(rate, 1e-6)
                print(f"  frame {f + 1}/{n}  t={t:5.2f}s  unique={rendered}  {rate:.1f} fps  eta {eta:.0f}s",
                      flush=True)
        proc.stdin.close()
        rc = proc.wait()
    finally:
        TESS.close()
        plt.close(fig)
    if rc != 0:
        raise RuntimeError(f"ffmpeg exited {rc}")
    print(f"silent {mp4_path}: {n} frames, {n / FPS:.2f}s, {rendered} unique draws, {time.time() - t0:.1f}s")
    return n


def contact_sheet_from_final(mp4, out_path):
    # One representative frame per beat
    picks = [5.0, 18.5, 30.5, 40.5, 56.0, 67.5]
    labels = [
        "1  ·  0:00–0:10  ·  One node + 8 nearest neighbours",
        "2  ·  0:10–0:22  ·  Eight bisectors cut an octahedron",
        "3  ·  0:22–0:34  ·  Six planes truncate the corners",
        f"4  ·  0:34–0:44  ·  Volume 4 coord³  =  {VOL_3} V_P",
        "5  ·  0:44–1:04  ·  16 cells tile a 2×2×2 block",
        "6  ·  1:04–1:10  ·  End card",
    ]
    thumb_w, thumb_h = 640, 360
    bar_h, pad, title_h = 44, 14, 56
    cols, rows = 3, 2
    Wsheet = cols * thumb_w + (cols + 1) * pad
    Hsheet = title_h + rows * (thumb_h + bar_h) + (rows + 1) * pad
    tmps = []
    tmpdir = os.path.join(os.path.dirname(out_path), "_cs_tmp")
    os.makedirs(tmpdir, exist_ok=True)
    for i, ts in enumerate(picks):
        f = os.path.join(tmpdir, f"c{i}.png")
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mp4,
             "-frames:v", "1", "-vf", f"scale={thumb_w}:{thumb_h}", f],
            check=True,
        )
        tmps.append(f)
    sheet = Image.new("RGB", (Wsheet, Hsheet), BG)
    draw = ImageDraw.Draw(sheet)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_bar = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        font_title = font_bar = ImageFont.load_default()
    title = f"BCC Voronoi Cell  ·  70 s  ·  1080p30  ·  Node cell = {VOL_3} V_P  (HOP = {HOP})"
    draw.text((pad, 16), title, fill=FG, font=font_title)
    for i, (p, lab) in enumerate(zip(tmps, labels)):
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = title_h + pad + r * (thumb_h + bar_h + pad)
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (x, y))
        draw.rectangle([x, y + thumb_h, x + thumb_w, y + thumb_h + bar_h], fill=PANEL)
        draw.text((x + 12, y + thumb_h + 12), lab, fill=FG, font=font_bar)
    sheet.save(out_path, "JPEG", quality=90)
    shutil.rmtree(tmpdir, ignore_errors=True)
    print(f"contact sheet {out_path} ({Wsheet}x{Hsheet})")


def thumbnail(mp4, out_path, t=56.0):
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", mp4,
         "-frames:v", "1", "-vf", "scale=1280:720", out_path],
        check=True,
    )
    print(f"thumbnail {out_path} @ {t:.2f}s")


def write_timeline(out_dir):
    scenes = []
    acc = 0.0
    for name, dur, heading, cap in BEATS:
        scenes.append({"name": name, "start": acc, "dur": dur, "heading": heading, "caption": cap})
        acc += dur
    tl = {
        "total": TOTAL,
        "fps": FPS,
        "scenes": scenes,
        "hop": HOP,
        "cell_volume_VP": VOL_VP,
        "cell_volume_label": VOL_3,
        "cell_volume_4dp": VOL_4,
        "coord_unit_lP": COORD_UNIT,
        "cues": {
            "neighbour_ticks": [NN_T0 + i * NN_DT for i in range(8)],
            "plane_times": [STARTS[1] + PL_T0 + i * PL_DT for i in range(8)],
            "octahedron_lock": STARTS[1] + OCT_LOCK_LOCAL,
            "second_neighbour_ticks": [STARTS[2] + SEC_T0 + i * SEC_DT for i in range(6)],
            "cut_times": [STARTS[2] + CUT_T0 + i * CUT_DT for i in range(6)],
            "faces_label": STARTS[2] + LEGEND3_T0,
            "volume_box": STARTS[3] + 3.40,
            "cell_pops": [STARTS[4] + (i + 0.15) * (POP_DUR - POP_FADE) / 16.0 for i in range(16)],
            "orbit_start": STARTS[4] + ORBIT_T0,
        },
    }
    path = os.path.join(out_dir, "timeline.json")
    json.dump(tl, open(path, "w"), indent=1)
    return tl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--thumb-t", type=float, default=56.0)
    args = ap.parse_args()
    out = args.out_dir
    os.makedirs(out, exist_ok=True)
    write_timeline(out)
    print(f"HOP={HOP}  cell_volume_VP={VOL_VP}  label={VOL_3} V_P  (4dp {VOL_4})")
    if args.preview or not (args.render or args.audio_only):
        # default: previews; --render does the full encode
        if args.preview or not (args.render or args.audio_only):
            preview(out)
            if not args.render:
                return
    silent = os.path.join(out, "_silent.mp4")
    final = os.path.join(out, "bcc_voronoi.mp4")
    wav = os.path.join(out, "bcc_voronoi_sfx.wav")
    if not args.audio_only:
        render_silent(out, silent, crf=args.crf)
    else:
        if not os.path.exists(final) and not os.path.exists(silent):
            raise SystemExit("audio-only needs an existing video")
        if os.path.exists(final) and not os.path.exists(silent):
            # strip audio to a silent copy for remux
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final, "-map", "0:v",
                            "-c", "copy", silent], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, "sfx_bcc_voronoi.py")], check=True)
    bv.loudnorm_mux(silent, wav, final, I=-16.0, TP=-2.0)
    if os.path.exists(silent):
        os.remove(silent)
    contact_sheet_from_final(final, os.path.join(out, "contact_sheet.jpg"))
    thumbnail(final, os.path.join(out, "thumbnail.png"), t=args.thumb_t)
    h = hashlib.sha256(open(final, "rb").read()).hexdigest()
    open(final + ".sha256", "w").write(f"{h}  bcc_voronoi.mp4\n")
    rep = bv.audio_report(final)
    # duration from the file, not just the nominal 70 s
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", final],
        capture_output=True, text=True, check=True,
    )
    rep["duration_s"] = float(probe.stdout.strip())
    rep["size_bytes"] = os.path.getsize(final)
    rep["sha256"] = h
    json.dump(rep, open(os.path.join(out, "audio_levels.json"), "w"), indent=1)
    print(final, rep)


if __name__ == "__main__":
    main()
