"""Measure the loop seam: how different is the last frame from the first?

A visible difference means the loop jumps every 4 seconds, which reads worse on a
hero banner than having no motion at all.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf8")


def find(name):
    p = shutil.which(name)
    if p:
        return p
    hits = list(Path(os.environ["LOCALAPPDATA"], "Microsoft/WinGet/Packages").rglob(name + ".exe"))
    return str(hits[0])


FFMPEG, FFPROBE = find("ffmpeg"), find("ffprobe")


def run(a):
    return subprocess.run(a, capture_output=True, text=True, encoding="utf8", errors="replace")


def mean_abs_diff(a, b, step=7):
    pa, pb = pymupdf.Pixmap(a), pymupdf.Pixmap(b)
    if pa.width != pb.width or pa.height != pb.height:
        return None, None
    total = 0
    worst = 0
    n = 0
    for y in range(0, pa.height, step):
        for x in range(0, pa.width, step):
            ca, cb = pa.pixel(x, y), pb.pixel(x, y)
            d = max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1]), abs(ca[2] - cb[2]))
            total += d
            worst = max(worst, d)
            n += 1
    return total / n, worst


print(f"{'clip':<24} {'dur':>6}  {'mean Δ':>7} {'max Δ':>6}   verdict")
for src in ("Videos/Banner 16x9.mp4", "Videos/Banner 9x16.mp4",
            "banner.mp4", "banner-portrait.mp4"):
    dur = float(run([FFPROBE, "-v", "quiet", "-show_entries", "format=duration",
                     "-of", "csv=p=0", src]).stdout.strip())

    # forward seek to one frame before the end; -sseof silently produced nothing here
    fps = 24.0
    last_t = max(0.0, dur - (1.5 / fps))

    r1 = run([FFMPEG, "-y", "-v", "error", "-i", src, "-frames:v", "1", "_seam_first.png"])
    r2 = run([FFMPEG, "-y", "-v", "error", "-ss", f"{last_t:.3f}", "-i", src,
              "-frames:v", "1", "_seam_last.png"])
    for tag, r in (("first", r1), ("last", r2)):
        if r.returncode != 0:
            print(f"  ffmpeg failed extracting {tag} frame: {r.stderr.strip()[:160]}")
    if not (Path("_seam_first.png").exists() and Path("_seam_last.png").exists()):
        print(f"{Path(src).name:<22} could not extract both frames, skipping")
        continue

    mean, worst = mean_abs_diff("_seam_first.png", "_seam_last.png")

    # 0-255 per channel. Under ~4 mean is imperceptible on a dark, soft image.
    if mean is None:
        verdict = "size mismatch"
    elif mean < 4:
        verdict = "seamless, loop as-is"
    elif mean < 12:
        verdict = "slight seam, crossfade it"
    else:
        verdict = "visible jump, crossfade required"

    print(f"{Path(src).name:<24} {dur:>5.2f}s  {mean:>7.2f} {worst:>6}   {verdict}")

for f in ("_seam_first.png", "_seam_last.png"):
    Path(f).unlink(missing_ok=True)
