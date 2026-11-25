"""Build the GitHub Pages video library in docs/.

    python publish.py                 # render approved videos in HD, then publish
    python publish.py --skip-render   # publish existing HD renders only
    python publish.py --only unjc-vs-unc

Reads library.json. Only entries with "status": "approved" are published,
because the Pages site is public. Change a video to "approved" only after its
figures have been checked against the standard and the print.

For each approved video this writes, into docs/videos/:
  <id>.mp4  (HD render, re-muxed with faststart so it streams)
  <id>.vtt  (captions converted from Manim's .srt)
  <id>.jpg  (thumbnail)
and then writes docs/library.json for the page to read.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
OUT = DOCS / "videos"
QUALITY_FLAG, QUALITY_DIR = "-qh", "1080p60"


def render(entry):
    print(f"Rendering {entry['scene']} ({entry['file']}) in HD...")
    subprocess.run([sys.executable, "-m", "manim", QUALITY_FLAG, entry["file"], entry["scene"]],
                   cwd=ROOT, check=True)


def rendered_paths(entry):
    folder = ROOT / "media" / "videos" / Path(entry["file"]).stem / QUALITY_DIR
    return folder / f"{entry['scene']}.mp4", folder / f"{entry['scene']}.srt"


def srt_to_vtt(srt_text):
    body = re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", srt_text.replace("\r\n", "\n"))
    return "WEBVTT\n\n" + body.strip() + "\n"


def duration_seconds(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(mp4)], capture_output=True, text=True, check=True)
    return int(float(out.stdout.strip()))  # round down, like the browser's player does


def publish(entry):
    mp4, srt = rendered_paths(entry)
    if not mp4.exists():
        raise SystemExit(f"Missing HD render for {entry['id']}: {mp4}\n"
                         f"Run without --skip-render, or: python -m manim -qh {entry['file']} {entry['scene']}")
    vid = entry["id"]
    dest = OUT / f"{vid}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-c", "copy",
                    "-movflags", "+faststart", str(dest)], check=True)
    dur = duration_seconds(dest)
    # Thumbnail from about 40% in, past the intro.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(dur * 0.4), "-i", str(dest),
                    "-frames:v", "1", "-vf", "scale=640:-1", "-q:v", "4", str(OUT / f"{vid}.jpg")],
                   check=True)
    captions = None
    if srt.exists():
        (OUT / f"{vid}.vtt").write_text(srt_to_vtt(srt.read_text(encoding="utf-8")), encoding="utf-8")
        captions = f"videos/{vid}.vtt"
    size_mb = dest.stat().st_size / 1e6
    print(f"  {vid}: {dur}s, {size_mb:.1f} MB")
    if size_mb > 90:
        print("  WARNING: GitHub rejects files over 100 MB.")
    return {
        "id": vid, "title": entry["title"], "topic": entry.get("topic", ""),
        "description": entry.get("description", ""), "duration": dur,
        "video": f"videos/{vid}.mp4", "poster": f"videos/{vid}.jpg", "captions": captions,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-render", action="store_true", help="use existing HD renders")
    ap.add_argument("--only", metavar="ID", help="publish just this video id (others stay as they are)")
    args = ap.parse_args()

    entries = json.loads((ROOT / "library.json").read_text(encoding="utf-8"))["videos"]
    approved = [e for e in entries if e.get("status") == "approved"]
    for e in entries:
        if e.get("status") != "approved":
            print(f"Skipping {e['id']} (status: {e.get('status', 'none')})")

    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "assets" / "apw_logo.png", DOCS / "apw_logo.png")
    (DOCS / ".nojekyll").touch()

    published_file = DOCS / "library.json"
    previous = {}
    if published_file.exists():
        previous = {v["id"]: v for v in json.loads(published_file.read_text(encoding="utf-8"))["videos"]}

    results = []
    for e in approved:
        if args.only and e["id"] != args.only:
            if e["id"] in previous:
                results.append(previous[e["id"]])
            continue
        if not args.skip_render:
            render(e)
        results.append(publish(e))

    # Remove published files for videos no longer approved.
    keep = {r["id"] for r in results}
    for f in OUT.iterdir():
        if f.stem not in keep:
            print(f"Removing {f.name} (no longer approved)")
            f.unlink()

    published_file.write_text(json.dumps({"videos": results}, indent=2) + "\n", encoding="utf-8")
    print(f"Published {len(results)} video(s) to {DOCS}")


if __name__ == "__main__":
    main()
