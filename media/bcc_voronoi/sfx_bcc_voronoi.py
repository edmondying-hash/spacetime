#!/usr/bin/env python3
"""Synthesized SFX for bcc_voronoi.mp4 (original numpy synthesis, no samples)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/workspace/bcc_test4_videos/v2_sound/_common")
from sfxlib import *

tl = load(HERE)
total = tl["total"]
cues = tl["cues"]
scenes = {s["name"]: s for s in tl["scenes"]}
m = Mix(total, seed=20261120)

# Quiet bed under the whole piece, slight lifts on later beats
m.add(hum(total, f0=49.0, amp=0.028, lfo=0.17,
          level_pts=((0, 0), (1.0, 1), (44, 1), (50, 0.85), (64, 0.7), (70, 0))), 0.0)
m.add(pad(total, (98, 147, 196), 0.022), 0.0)

# Beat 1: eight soft ticks as neighbours appear
for i, t0 in enumerate(cues["neighbour_ticks"]):
    freq = 1320 * (1.04 ** i)
    m.add(tick(freq, 0.035), t0, pan=-0.35 + 0.1 * i)

# Beat 2: airy whoosh as each plane arrives; chord when the octahedron locks
for i, t0 in enumerate(cues["plane_times"]):
    m.add(whoosh(0.55, 240, 1800, 0.045, falling=False), t0, pan=-0.4 + 0.1 * i)
m.add(chime(523.25, 2.2, 0.07), cues["octahedron_lock"], pan=0.0)  # C5, muted
m.add(chime(659.25, 2.0, 0.04), cues["octahedron_lock"] + 0.04, pan=0.15)

# Beat 3: six dry clicks as the square cuts land; resolve when 14 faces appears
for i, t0 in enumerate(cues["cut_times"]):
    m.add(click(freq=1900 + 80 * i, amp=0.055, rng=m.rng), t0, pan=-0.3 + 0.12 * i)
m.add(chime(784.0, 2.4, 0.065), cues["faces_label"], pan=0.05)

# Beat 4: quiet held tone under the numbers — no sting on the V_P label
m.add(pad(10.0, (110, 165, 220), 0.028), scenes["volume"]["start"])
m.add(hum(10.0, f0=73.4, amp=0.02, lfo=0.2), scenes["volume"]["start"])

# Beat 5: soft pops as cells appear, airy drone under the orbit
for i, t0 in enumerate(cues["cell_pops"]):
    m.add(tick(980 + 18 * i, 0.028), t0, pan=-0.4 + 0.05 * (i % 16))
m.add(pad(14.5, (87, 130.8, 174), 0.03), cues["orbit_start"])
m.add(hum(14.5, f0=43.6, amp=0.022, lfo=0.12), cues["orbit_start"])

# End card: pad fades with Mix.write fade_out
m.add(pad(6.2, (98, 147, 196), 0.04), scenes["end"]["start"])
m.add(chime(660, 2.6, 0.04), scenes["end"]["start"] + 0.3)

m.write(os.path.join(HERE, "bcc_voronoi_sfx.wav"), fade_out=1.4)
print("sfx ok")
