"""Confirm the generator watermark is gone from every shipped asset.

Google Flow stamps a four-pointed sparkle into the lower right of its output. An
absolute brightness test gives false positives, because some scenes are legitimately
bright in that corner (the lit architectural model, the clinic's daylight). So this
compares the SAME content in the source and in the shipped file: if the local
brightness excess drops sharply, delogo did its job.
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


FFMPEG = find("ffmpeg")

# The delogo box, as fractions, matching build-assets.py (x=1108 y=558 w=94 h=88 of 1280x720)
WM_BOX = (1108 / 1280, 558 / 720, 94 / 1280, 88 / 720)
# A control box of the same size elsewhere in frame, expected to be untouched
CTRL_BOX = (0.06, 0.558, 94 / 1280, 88 / 720)


def run(a):
    return subprocess.run(a, capture_output=True, text=True, encoding="utf8", errors="replace")


def luma(px):
    return 0.2126 * px[0] + 0.7152 * px[1] + 0.0722 * px[2]


def region_diff(png_a, png_b, box):
    """Mean absolute luma difference inside a box, between two same-size frames.

    Re-encoding shifts every pixel slightly, so an absolute number means nothing on
    its own. It only becomes meaningful next to a control region.
    """
    pa, pb = pymupdf.Pixmap(png_a), pymupdf.Pixmap(png_b)
    if (pa.width, pa.height) != (pb.width, pb.height):
        return None
    W, H = pa.width, pa.height
    fx, fy, fw, fh = box
    x0, y0 = int(fx * W), int(fy * H)
    x1, y1 = min(int((fx + fw) * W), W), min(int((fy + fh) * H), H)

    tot = n = 0
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            tot += abs(luma(pa.pixel(x, y)) - luma(pb.pixel(x, y)))
            n += 1
    return tot / n if n else None


def frame(path, t, out):
    run([FFMPEG, "-y", "-v", "error", "-ss", f"{t}", "-i", path, "-frames:v", "1", out])
    return Path(out).exists()


# (label, source file, source t, shipped file, shipped t)
PAIRS = [
    ("real estate", "Videos/Real estate 16x9.mp4", 1.0,  "scrub.mp4", 1.0),
    ("electronics", "Videos/Mobile 16x9.mp4",      2.0,  "scrub.mp4", 10.0),
    ("clinical",    "Videos/Dental 16x9.mp4",      2.5,  "scrub.mp4", 18.5),
    ("banner",      "Videos/Banner 16x9.mp4",      1.0,  "banner.mp4", 1.0),
]

print("Comparing the watermark region against a control region, source vs shipped.")
print("The watermark box should differ far more than the control, which only sees")
print("re-encode noise.\n")
print(f"{'scene':<14} {'wm Δ':>7} {'control Δ':>10} {'ratio':>7}  verdict")
fails = []
for label, src, st, dst, dt in PAIRS:
    if not (Path(src).exists() and Path(dst).exists()):
        print(f"{label:<14} missing input, skipped")
        continue
    if not (frame(src, st, "_wm_a.png") and frame(dst, dt, "_wm_b.png")):
        print(f"{label:<14} could not extract frames, skipped")
        continue

    d_wm = region_diff("_wm_a.png", "_wm_b.png", WM_BOX)
    d_ct = region_diff("_wm_a.png", "_wm_b.png", CTRL_BOX)
    if d_wm is None or d_ct is None:
        print(f"{label:<14} frame size mismatch, skipped")
        continue

    ratio = d_wm / d_ct if d_ct > 0.01 else float("inf")
    ok = ratio >= 2.5
    print(f"{label:<14} {d_wm:>7.2f} {d_ct:>10.2f} {ratio:>7.1f}  "
          f"{'delogo applied' if ok else 'NOT STRIPPED'}")
    if not ok:
        fails.append(f"{label}: watermark region changed only {ratio:.1f}x the control")

for f in ("_wm_a.png", "_wm_b.png"):
    Path(f).unlink(missing_ok=True)

print()
if fails:
    print("FAILURES")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("Generator watermark removed from every shipped asset.")
