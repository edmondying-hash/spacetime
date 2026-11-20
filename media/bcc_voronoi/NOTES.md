# bcc_voronoi.mp4 — The BCC Node Voronoi Cell

70 s · 1920×1080 @ 30 fps · H.264 + AAC 192k · dark chrome, channel mark lower right.

Source geometry: `bcc/plot_bcc_3d_cell.build_truncated_octahedron_faces()` from
[edmondying-hash/spacetime](https://github.com/edmondying-hash/spacetime) (unchanged
through main `0e019e7`). Box copies in `src/` (sha256 `4010e75f…` for the plot
script, `43ed0aa5…` for `bcc_config.py`), matching
`/workspace/spacetime_upload/v7/ed_extract/spacetime`.

Volume label is read at render time from `bcc_config.DERIVED['cell_volume_VP']`
under the locked default `HOP="lP"` (no `BCC_HOP` override): 0.7698003589…,
shown on screen as **0.770 V_P** (`f"{VOL:.3f}"`). The exact value
`4/(3√3) = 0.7698` is also shown on the volume beat. This is the model's OD1
unit convention, not a prediction. The geometric fact, kept separate, is
**4 coord³ = half the conventional cube of side 2**.

## Structure

| Beat | Time | Content |
|---|---|---|
| 1 | 0:00–0:10 | One node + 8 nearest neighbours `(±1, ±1, ±1)`, distance √3 |
| 2 | 0:10–0:22 | 8 perpendicular bisectors cut a regular octahedron (vertices at ±1.5 on the axes) |
| 3 | 0:22–0:34 | 6 second-neighbour planes (`\|x\|,|y|,|z| = 1`) truncate the tips; 8 hexagons + 6 squares = 14 faces |
| 4 | 0:34–0:44 | Volume 4 coord³, then the 0.770 V_P / HOP=lP unit box |
| 5 | 0:44–1:04 | 16 cells pop in on a 2×2×2 conventional block, then a slow orbit |
| 6 | 1:04–1:10 | End card |

## Where the numbers come from

| On screen | Source |
|---|---|
| 8 neighbours `(±1, ±1, ±1)`, distance √3 | BCC lattice with conventional cube side 2 |
| Octahedron vertices `(±1.5, 0, 0)` cyclic | Perpendicular bisectors of the 8 body diagonals, planes `±x±y±z = 1.5` |
| 8 hexagons, 6 squares, 14 faces | scipy Voronoi on that lattice (verified; vertices match the source mesh) |
| 4 coord³, measured volume = 4.000 | ConvexHull of the Voronoi vertices; also half of 2³; also octahedron 4.5 minus six pyramids of 1/12 |
| Node cell = 0.770 V_P, HOP = lP | `cfg.HOP` and `f"{cfg.DERIVED['cell_volume_VP']:.3f}"` |
| 4/(3√3) = 0.7698 | same DERIVED value at 4 decimals; `cell_volume_VP = 4 * (l_P/√3)³` |
| 16 sites, 2×2×2 conventional cells | all-even and all-odd sites with coordinates in {0,1,2,3}, centred |

Nothing is called “predicted”. Geometry beats are not stamped TOY MODEL. When
V_P / HOP / l_P appear, the picture says they are a unit convention.

## Renderer

Beats 1–4 and the end card: matplotlib 3D frames piped to ffmpeg (same chrome
pipeline as the mercury video). Beat 5 (tessellation orbit): pyvista offscreen
with depth peeling, composited into the same chrome. Matplotlib's transparency
sort was muddy at some orbit angles in the storyboard stills and in preview;
pyvista is the fallback named in the brief. The persistent pyvista plotter is
updated in place (camera + per-cell opacity); do not call
`reset_camera_clipping_range()`, which made the transparent cells vanish under
depth peeling.

Sound: synthesized in `sfx_bcc_voronoi.py` (sfxlib, no samples) — pad/hum bed,
ticks as neighbours appear, whooshes as bisector planes arrive, a muted chord
when the octahedron locks, dry clicks on the six square cuts, a resolve when
“14 faces” appears, a quiet tone under the volume numbers (no sting on the
V_P label), pops as cells appear, a drone under the orbit. Mastered with
`bccvid.loudnorm_mux` to −16 LUFS integrated, limiter at −3 dB; measured
true peak −3.0 dBTP.

## Files

```text
/workspace/spacetime_videos/bcc_voronoi/
  bcc_voronoi.mp4
  bcc_voronoi.mp4.sha256
  bcc_voronoi_sfx.wav
  thumbnail.png          # 1280×720 from t = 56 s (orbit)
  contact_sheet.jpg      # 3×2 from the finished video
  audio_levels.json
  timeline.json
  NOTES.md
  render_bcc_voronoi.py
  sfx_bcc_voronoi.py
  src/bcc_config.py
  src/plot_bcc_3d_cell.py
```

sha256 `0fbc9efc2cd81e2e4e8e714dbe453a495c116865ac1bf12ec9ee514996c6efc1`
· 7,059,138 bytes (6.73 MiB) · 70.00 s · −16.0 LUFS · −3.0 dBTP.
