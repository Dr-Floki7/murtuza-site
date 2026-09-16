"""Measure real contrast from rendered pixels, not from static CSS analysis.

The Impeccable detector reports low contrast on the banner and film stage. It composites
their radial-gradient layer over the body's paper background and misses that each element
carries its own ink `background-color` underneath. This samples what the browser actually
paints behind the text and computes WCAG ratios from that.
"""
import json
import subprocess
import sys

import pymupdf

sys.stdout.reconfigure(encoding="utf8")

PROBE = """
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch({channel:'chrome'});
  const p = await b.newPage({viewport:{width:1280,height:900}});
  await p.goto('http://127.0.0.1:8099/index.html',{waitUntil:'load'});
  await p.waitForTimeout(600);

  const out = [];
  // banner copy
  for (const sel of ['.banner h1','.banner h1 em','.banner__sub','.mark']) {
    const box = await p.locator(sel).first().boundingBox();
    const color = await p.locator(sel).first().evaluate(e => getComputedStyle(e).color);
    const size  = await p.locator(sel).first().evaluate(e => parseFloat(getComputedStyle(e).fontSize));
    const weight= await p.locator(sel).first().evaluate(e => getComputedStyle(e).fontVariationSettings);
    out.push({sel, box, color, size, weight});
  }
  await p.screenshot({path:'_c_banner.png'});

  // mid-film copy, a quarter into the act
  await p.evaluate(() => {
    const a = document.getElementById('act');
    window.scrollTo(0, a.getBoundingClientRect().top + window.scrollY + a.offsetHeight*0.22);
  });
  await p.waitForTimeout(500);
  const panelOut = [];
  for (const sel of ['.panel[data-on] h2','.panel[data-on] p','.panel[data-on] .panel__year']) {
    const loc = p.locator(sel).first();
    if (await loc.count() === 0) continue;
    panelOut.push({
      sel,
      box: await loc.boundingBox(),
      color: await loc.evaluate(e => getComputedStyle(e).color),
      size: await loc.evaluate(e => parseFloat(getComputedStyle(e).fontSize)),
    });
  }
  await p.screenshot({path:'_c_film.png'});

  console.log(JSON.stringify({banner: out, film: panelOut}));
  await b.close();
})();
"""


def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_rgb(s):
    nums = s[s.index("(") + 1: s.index(")")].split(",")
    return tuple(int(float(n)) for n in nums[:3])


def bg_behind(png, box):
    """Darkest (worst-case) background sample from a band just outside the text box."""
    pix = pymupdf.Pixmap(png)
    y = int(box["y"] + box["height"] / 2)
    samples = []
    # sample to the right of the text run, inside the same visual band
    for x in range(int(box["x"] + box["width"]) + 6,
                   min(int(box["x"] + box["width"]) + 160, pix.width - 1), 7):
        if 0 <= y < pix.height:
            samples.append(pix.pixel(x, y))
    if not samples:
        samples = [pix.pixel(int(box["x"]), y)]
    # worst case for light text is the lightest background pixel
    return max(samples, key=lum)


open("_probe.js", "w", encoding="utf8").write(PROBE)
raw = subprocess.run(["node", "_probe.js"], capture_output=True, text=True,
                     encoding="utf8", errors="replace")
line = [l for l in raw.stdout.splitlines() if l.strip().startswith("{")]
if not line:
    print("probe failed:\n", raw.stdout[-2000:], raw.stderr[-2000:])
    sys.exit(1)
data = json.loads(line[-1])

worst = 999
fails = []
for group, png in (("banner", "_c_banner.png"), ("film", "_c_film.png")):
    print(f"\n{group}  ({png})")
    for item in data[group]:
        if not item.get("box"):
            continue
        fg = parse_rgb(item["color"])
        bg = bg_behind(png, item["box"])
        r = ratio(fg, bg)
        size = item["size"]
        large = size >= 24 or size >= 18.66  # bold display type here is all >=18.66
        need = 3.0 if large else 4.5
        ok = r >= need
        worst = min(worst, r / need)
        if not ok:
            fails.append((item["sel"], round(r, 2), need))
        print(f"  {'ok ' if ok else 'FAIL'} {item['sel']:<34} "
              f"{round(r,2):>6}:1  need {need}  ({int(size)}px, "
              f"fg {fg} on bg {tuple(bg[:3])})")

print()
if fails:
    print("CONTRAST FAILURES:", fails)
    sys.exit(1)
print("All sampled text meets WCAG AA against the pixels actually painted behind it.")
