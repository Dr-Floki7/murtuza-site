"""Turn the raw Flow output in videos/ into the assets the page actually serves.

Run this again any time a clip is regenerated.

    python build-assets.py

Produces, in the project root:
    scrub.mp4           landscape, all-keyframe, for wide viewports
    scrub-portrait.mp4  portrait, all-keyframe, for phones held upright
    banner.webp         hero image, primary
    banner.jpg          hero image, fallback
    og-cover.jpg        1200x630 social preview

All-keyframe (keyint=1) is what makes scrubbing instant. A normal MP4 only seeks to
keyframes, so scrubbing a standard encode stutters badly. It costs roughly 5-10x the
file size, which is why the encode escalates CRF until it fits the budget below.

25 MiB is the budget because that is Cloudflare Pages' hard per-file limit. Staying under
it keeps that host a live option and keeps mobile load times honest.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf8")

ROOT = Path(__file__).parent
SRC = ROOT / "videos"
BUDGET_MB = 24.0          # stay under Cloudflare Pages' 25 MiB per-file hard limit
CRF_LADDER = [24, 27, 30, 33]

# `slow` buys very little on an all-intra encode (no inter-frame search to optimise)
# and costs minutes. `medium` is the honest trade here.
PRESET = "medium"

# Trim seconds off the START of a clip, never the end: each clip's final second is the
# designed move past the lens that hides the wardrobe change, and the very last frame of
# the last clip is what the call-to-action sits over. Empty means keep everything.
TRIM_HEAD = {}            # e.g. {"Real estate": 2.0, "Mobile": 2.0}

# Reverse chronological: this is the persuasive order, not the CV order.
ORDER = [
    ("Real estate", "real estate, 2025 to now"),
    ("Mobile",      "consumer electronics, 2022 to 2025"),
    ("Dental",      "clinical, 2013 to 2020"),
]


def find(name):
    """winget modified PATH but this shell has not been restarted."""
    p = shutil.which(name)
    if p:
        return p
    hits = list(Path(os.environ["LOCALAPPDATA"], "Microsoft/WinGet/Packages")
                .rglob(name + ".exe"))
    if not hits:
        sys.exit(f"{name} not found")
    return str(hits[0])


FFMPEG, FFPROBE = find("ffmpeg"), find("ffprobe")


def run(args):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-2500:])
        sys.exit(f"failed: {' '.join(str(a) for a in args[:6])} ...")
    return r


def probe(path):
    """Returns (duration, width, height). Duration is 0.0 for stills, which carry none."""
    r = run([FFPROBE, "-v", "quiet", "-print_format", "json",
             "-show_entries", "stream=width,height:format=duration",
             "-select_streams", "v:0", str(path)])
    d = json.loads(r.stdout)
    return (float(d.get("format", {}).get("duration", 0.0) or 0.0),
            d["streams"][0]["width"], d["streams"][0]["height"])


def resolve(stem, ratio):
    """Filenames vary in capitalisation, so match case-insensitively."""
    want = f"{stem} {ratio}".lower()
    for f in SRC.glob("*.mp4"):
        if f.stem.lower() == want:
            return f
    sys.exit(f"missing clip: {stem} {ratio}.mp4 in {SRC}")


def build(ratio, out_name, scale):
    clips = [resolve(stem, ratio) for stem, _ in ORDER]

    print(f"\n{'='*66}\n{out_name}  ({ratio})\n{'='*66}")
    durations = []
    for (stem, label), f in zip(ORDER, clips):
        dur, w, h = probe(f)
        durations.append(dur)
        print(f"  {f.name:<24} {w}x{h}  {dur:>5.2f}s   {label}")

    # optional head trims, applied before concat so the join stays a stream copy
    staged = []
    for (stem, _), c in zip(ORDER, clips):
        head = TRIM_HEAD.get(stem, 0)
        if not head:
            staged.append(c)
            continue
        cut = ROOT / f"_cut_{ratio}_{stem.replace(' ', '')}.mp4"
        run([FFMPEG, "-y", "-v", "error", "-ss", str(head), "-i", str(c),
             "-c", "copy", "-avoid_negative_ts", "make_zero", str(cut)])
        print(f"  trimmed {head}s off the head of {c.name} -> {probe(cut)[0]:.2f}s")
        staged.append(cut)

    listing = ROOT / f"_concat_{ratio}.txt"
    listing.write_text("".join(
        f"file '{c.as_posix()}'\n" for c in staged), encoding="utf8")
    joined = ROOT / f"_joined_{ratio}.mp4"
    run([FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c", "copy", str(joined)])
    durations = [probe(c)[0] for c in staged]

    total, jw, jh = probe(joined)
    print(f"  joined: {jw}x{jh}  {total:.2f}s")

    out = ROOT / out_name
    for crf in CRF_LADDER:
        run([FFMPEG, "-y", "-v", "error", "-i", str(joined),
             "-an",                                   # audio stripped, page never needs it
             "-vf", scale,
             "-c:v", "libx264", "-preset", PRESET, "-crf", str(crf),
             "-pix_fmt", "yuv420p",
             "-x264-params", "keyint=1:min-keyint=1:scenecut=0",
             "-movflags", "+faststart",
             str(out)])
        mb = out.stat().st_size / 1024 / 1024
        verdict = "fits" if mb <= BUDGET_MB else "over budget, escalating"
        print(f"  crf {crf}: {mb:6.2f} MB   {verdict}")
        if mb <= BUDGET_MB:
            break
    else:
        print(f"  WARNING: still {mb:.2f} MB at crf {CRF_LADDER[-1]}")

    listing.unlink(missing_ok=True)
    joined.unlink(missing_ok=True)
    for f in ROOT.glob(f"_cut_{ratio}_*.mp4"):
        f.unlink(missing_ok=True)
    return total, durations, out.stat().st_size / 1024 / 1024


land_total, land_durs, land_mb = build("16x9", "scrub.mp4", "scale=1280:-2")
port_total, port_durs, port_mb = build("9x16", "scrub-portrait.mp4", "scale=720:-2")

# ── banner loops ──────────────────────────────────────────────────────────
def build_banner(ratio, out_name):
    """Ping-pong the clip so the loop is seamless by construction.

    The raw clips do not loop: measured mean pixel difference between last and first
    frame is ~15 (landscape) and ~79 (portrait), which reads as a visible jump every
    four seconds. Playing forward then reversed removes the seam entirely, and with
    only breathing and a slow drift in shot the reversal is imperceptible.

    Not all-keyframe: this one autoplays rather than being scrubbed, so it gets a
    normal encode and stays small.
    """
    src = None
    for f in SRC.glob("*.mp4"):
        if f.stem.lower() == f"banner {ratio}".lower():
            src = f
            break
    if not src:
        print(f"  no banner clip for {ratio}, skipping")
        return None

    dur, w, h = probe(src)
    out = ROOT / out_name
    run([FFMPEG, "-y", "-v", "error", "-i", str(src),
         "-an",
         "-filter_complex",
         "[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0[v]",
         "-map", "[v]",
         "-c:v", "libx264", "-preset", PRESET, "-crf", "24",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(out)])
    odur, ow, oh = probe(out)
    print(f"  {src.name:<22} {w}x{h} {dur:.2f}s  ->  {out_name} "
          f"{ow}x{oh} {odur:.2f}s  {out.stat().st_size/1024/1024:.2f} MB  (ping-pong)")
    return out


print(f"\n{'='*66}\nbanner loops\n{'='*66}")
build_banner("16x9", "banner.mp4")
build_banner("9x16", "banner-portrait.mp4")

# ── stills ────────────────────────────────────────────────────────────────
banner_src = SRC / "Banner.png"
print(f"\n{'='*66}\nstills\n{'='*66}")
if banner_src.exists():
    run([FFMPEG, "-y", "-v", "error", "-i", str(banner_src),
         "-vf", "scale=2560:-2:flags=lanczos", "-q:v", "3",
         str(ROOT / "banner.jpg")])
    run([FFMPEG, "-y", "-v", "error", "-i", str(banner_src),
         "-vf", "scale=2560:-2:flags=lanczos", "-quality", "82",
         str(ROOT / "banner.webp")])
    # social preview: crop to 1200x630 around the centre figure
    run([FFMPEG, "-y", "-v", "error", "-i", str(banner_src),
         "-vf", "scale=1200:-2:flags=lanczos,crop=1200:630:0:(ih-630)/2",
         "-q:v", "3", str(ROOT / "og-cover.jpg")])
    for f in ("banner.jpg", "banner.webp", "og-cover.jpg"):
        p = ROOT / f
        _, w, h = probe(p)
        print(f"  {f:<16} {w}x{h}  {p.stat().st_size/1024:7.1f} KB")
else:
    print(f"  WARNING: {banner_src} not found, skipping stills")

# ── the numbers the page needs ────────────────────────────────────────────
print(f"\n{'='*66}\nCALIBRATION — stage boundaries as fractions of total\n{'='*66}")
print(f"landscape total {land_total:.2f}s   portrait total {port_total:.2f}s")
if abs(land_total - port_total) > 0.15:
    print("  NOTE: the two cuts differ in length; bands below use the landscape cut.")

acc = 0.0
bounds = []
for (stem, label), d in zip(ORDER, land_durs):
    start, end = acc / land_total, (acc + d) / land_total
    bounds.append((stem, start, end))
    print(f"  {stem:<12} {acc:>5.2f}s to {acc+d:>5.2f}s   "
          f"progress {start:.3f} to {end:.3f}   {label}")
    acc += d

print("\nsuggested panelFor() bands, inset so the film breathes between captions:")
for i, (stem, s, e) in enumerate(bounds):
    span = e - s
    lo, hi = s + span * 0.16, e - span * 0.12
    print(f"  panel {i} ({stem:<12}): p >= {lo:.3f} && p < {hi:.3f}")

print(f"\ntotal shipped video: {land_mb:.1f} MB + {port_mb:.1f} MB "
      f"(one per device, never both)")
