# APW Training Videos

Narrated training videos for American Precision Works (APW), a precision CNC machine shop. Videos are built with Manim (Community edition) and manim-voiceover, and play for new hires and on shop-floor screens.

## Environment

- Windows, PowerShell, Python 3.12 (Manim 0.22)
- The `py` launcher is NOT installed. Always use `python -m ...`
- FFmpeg installed via winget
- Packages: `manim`, `manim-voiceover[gtts]`, `piper-tts`
- Narration voice: Piper `en_GB-northern_english_male-medium`, offline, via `piper_service.py`. Models live in `voices/` (git-ignored); on a new PC run `python -m piper.download_voices --download-dir voices en_GB-northern_english_male-medium`. Without the model, `APWScene` falls back to gTTS (needs internet). Voice and pace are set by `VOICE_MODEL` / `VOICE_PACE` in `apw_style.py`.

## Rendering

- Quick test (low quality, fast): `python -m manim -pql <file>.py <SceneName>`
- Final HD: `python -m manim -pqh <file>.py <SceneName>`
- Output lands in `media/videos/<file>/<quality>/` as MP4
- Always do a low-quality test render before HD

## Current scenes

| File | Scene | Topic |
|---|---|---|
| `photo.py` | `Photolithography` | Test video: photolithography process, 8 steps |
| `unjc.py` | `UNJCvsUNC` | UNJC vs UNC threads, focused on internal thread dimensions |
| `style_demo.py` | `StyleDemo` | Check that the house style renders |
| `tp1_basics.py` | `TP1Basics` | True position 1/5: basics, square vs round zone, the formula |
| `tp2_datums.py` | `TP2Datums` | True position 2/5: one, two, three datums, datum order |
| `tp3_3d.py` | `TP3ThreeD` | True position 3/5: cylindrical zone, tilt, width zones, coaxial |
| `tp4_modifiers.py` | `TP4Modifiers` | True position 4/5: MMC, LMC, bonus, virtual condition, datum shift |
| `tp5_threads.py` | `TP5Threads` | True position 5/5: threaded holes, projected zones, fastener formulas |

The true position series shares helpers in `tp_common.py` (FCF builder, GD&T symbols, dimensions, simple 3D projection). Its sources and open fact-check items are in `notes/true_position_sources.md`; John approved and published the five entries on 2026-11-25 with those fact-check items still open.

## Video library (GitHub Pages)

The repo is public, so the Pages site is public. `docs/` is the site, served by GitHub Pages from `main` / `docs`.

- `library.json` lists every video (id, title, file, scene, topic, description, status)
- Only `"status": "approved"` videos are published. Set that only after the content has been checked (see Accuracy).
- `python publish.py` renders approved videos in HD and copies MP4, captions (.vtt) and a thumbnail into `docs/videos/`, then writes `docs/library.json`. `--skip-render` reuses existing HD renders; `--only <id>` updates one video.
- Commit `docs/` and push; Pages updates in a minute or two.
- Local preview: `python -m http.server 8765 --directory docs`, then open http://localhost:8765

## House style module

New videos subclass `APWScene` from `apw_style.py` (`from apw_style import *`). It sets up the narration voice (`make_voice()`) and provides `apw_intro()`, a corner logo, `apw_outro()`, meaning colors (`STANDARD`, `IMPROVED`, `PROBLEM`, `REF_A`, `REF_B`), company colors (`APW_*`, taken from the Tool Tag Generator CSS), and the helpers `apw_title`, `step_label`, `bullets` and `reveal_bullets`. The logo is `assets/apw_logo.png`, a 1200px copy of `apw-logo-stacked-blue.png` from the American-Precision-Works repo with a transparent background.

## Planned topics

- Collets
- Assembling tool holders (likely Blender, using models exported from Fusion 360)
- Other shop topics: thread wire measurement, GD&T callouts, work offsets, R650 pallet change

## Tool choice

- **Manim:** concept explainers (thread profiles, dimensions, processes)
- **Blender (scripted):** physical assembly steps using real parts exported from Fusion 360 as STL/OBJ
- Real bench footage can be mixed in for hands-on steps

## Visual style

- APW navy background (`APW_DARK`, set by `APWScene`), Segoe UI text
- Show parts as real geometry (sections through the axis so both sides show), not schematic squiggles
- Point at the area in question with `callout()` labels instead of bullet slides
- Keep transitions clean: Transform only between shapes built with the same point count; never Transform text (fade it)
- Color meaning is consistent across videos:
  - Blue = standard / baseline (e.g. UNC)
  - Green = improved / correct (e.g. UNJC)
  - Red = problem spots, failure points
  - Yellow / orange = related reference lines or dimensions that need telling apart
- White text; bullets fade in one at a time so viewers don't read ahead
- Each step gets one spoken line; animation `run_time` matches the voiceover duration

## To do

- Move `photo.py` and `unjc.py` onto `APWScene` from `apw_style.py`
- Optionally replace the Piper voice with John's own recorded narration (manim-voiceover's RecorderService)

## Accuracy

Technical content (thread classes, diameters, tolerances) must be checked against the governing standard (e.g. ASME B1.15 for UNJ) and the part print before a video is shown to anyone. Don't invent specific numeric limits; keep figures schematic unless John supplies real values.
