# APW Training Videos

Narrated training videos for American Precision Works (APW), a precision CNC machine shop. Videos are built with Manim (Community edition) and manim-voiceover, and play for new hires and on shop-floor screens.

## Environment

- Windows, PowerShell, Python 3.11
- The `py` launcher is NOT installed. Always use `python -m ...`
- FFmpeg installed via winget
- Packages: `manim`, `manim-voiceover[gtts]`
- gTTS needs an internet connection while rendering

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

## House style module

New videos subclass `APWScene` from `apw_style.py` (`from apw_style import *`). It sets up the gTTS voice and provides `apw_intro()`, a corner logo, `apw_outro()`, meaning colors (`STANDARD`, `IMPROVED`, `PROBLEM`, `REF_A`, `REF_B`), company colors (`APW_*`, taken from the Tool Tag Generator CSS), and the helpers `apw_title`, `step_label`, `bullets` and `reveal_bullets`. The logo is `assets/apw_logo.png`, a 1200px copy of `apw-logo-stacked-blue.png` from the American-Precision-Works repo with a transparent background.

## Planned topics

- Collets
- Assembling tool holders (likely Blender, using models exported from Fusion 360)
- Other shop topics: thread wire measurement, GD&T callouts, work offsets, R650 pallet change

## Tool choice

- **Manim:** concept explainers (thread profiles, dimensions, processes)
- **Blender (scripted):** physical assembly steps using real parts exported from Fusion 360 as STL/OBJ
- Real bench footage can be mixed in for hands-on steps

## Visual style

- Default Manim dark background
- Color meaning is consistent across videos:
  - Blue = standard / baseline (e.g. UNC)
  - Green = improved / correct (e.g. UNJC)
  - Red = problem spots, failure points
  - Yellow / orange = related reference lines or dimensions that need telling apart
- White text; bullets fade in one at a time so viewers don't read ahead
- Each step gets one spoken line; animation `run_time` matches the voiceover duration

## To do

- Move `photo.py` and `unjc.py` onto `APWScene` from `apw_style.py`
- Optionally swap gTTS for a better voice, or John's own recorded narration

## Accuracy

Technical content (thread classes, diameters, tolerances) must be checked against the governing standard (e.g. ASME B1.15 for UNJ) and the part print before a video is shown to anyone. Don't invent specific numeric limits; keep figures schematic unless John supplies real values.
