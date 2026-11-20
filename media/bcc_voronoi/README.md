# BCC Voronoi cell explainer

`bcc_voronoi.mp4` (1920x1080, 30 fps, 70 s) shows how the Voronoi cell of a BCC lattice node becomes a truncated octahedron — 8 hexagonal faces toward the nearest neighbours, 6 square faces toward the second neighbours — and how neighbouring cells tile space with no gaps.

- The volume **4 coord³** is standard BCC geometry: half the conventional cube of side 2.
- The on-screen label **0.770 V_P** is the model's OD1 unit convention with the locked default `HOP = "lP"` in `bcc_config.py` (1 coord = l_P/√3, so 4/(3√3) ≈ 0.7698, shown as 0.770). It is a unit choice, not a prediction. The value is read from `bcc_config.DERIVED["cell_volume_VP"]`.
- Face geometry comes from `bcc/plot_bcc_3d_cell.py` and was checked independently with scipy Voronoi.
- Sound is synthesized (no samples).

See [NOTES.md](NOTES.md) for timings, where each on-screen number comes from, and the sha256 of this encode.

## Re-render

```bash
python3 render_bcc_voronoi.py --render
```

Needs Python 3 with matplotlib, numpy, pyvista, Pillow, and ffmpeg. The tessellation orbit uses pyvista (matplotlib's transparency sort was muddy mid-orbit). Do not set `BCC_HOP`; the locked default `HOP=lP` is required for the 0.770 V_P label.

The scripts still point at the machine paths used when this video was made:

- config and face builder: `/workspace/spacetime_upload/v7/ed_extract/spacetime` (in this repo those files are `bcc_config.py` and `bcc/plot_bcc_3d_cell.py`)
- shared render/audio helpers: `/workspace/bcc_test4_videos/v2_sound/_common` (`bccvid`, `sfxlib`)
- channel mark: `/workspace/watermark/b_dark.png`

Point those at the repo root, the shared helpers, and the watermark before re-rendering elsewhere. Loudness target is -16 LUFS integrated, true peak at most -2 dBTP.

Files: `bcc_voronoi.mp4`, `thumbnail.png`, `contact_sheet.jpg`, `render_bcc_voronoi.py`, `sfx_bcc_voronoi.py`, `timeline.json`, `audio_levels.json`.
