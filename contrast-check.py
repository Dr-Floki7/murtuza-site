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

PROBE = r"""
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch({channel:'chrome'});
  const p = await b.newPage({viewport:{width:1280,height:900}});
  await p.goto('http://127.0.0.1:8099/index.html',{waitUntil:'load'});
  await p.waitForTimeout(600);

  const read = async (sel) => {
    const loc = p.locator(sel).first();
    if (await loc.count() === 0) return null;
    return {
      sel,
      box: await loc.boundingBox(),
      color: await loc.evaluate(e => getComputedStyle(e).color),
      size: await loc.evaluate(e => parseFloat(getComputedStyle(e).fontSize)),
      // resolved weight: the variable-font axis wins over the `font-weight` keyword
      weight: await loc.evaluate(e => {
        const cs = getComputedStyle(e);
        const m = /"wght"\s+(\d+)/.exec(cs.fontVariationSettings || '');
        return m ? parseInt(m[1], 10) : parseInt(cs.fontWeight, 10) || 400;
      }),
    };
  };

  /* The banner is a two-beat reveal: at scroll 0 the copy is hidden and the veil is
     transparent. Measure the state a visitor actually reads, with the copy fully on
     and the veil at full strength. */
  await p.evaluate(() => {
    const b = document.getElementById('banner');
    window.scrollTo({ top: (b.offsetHeight - window.innerHeight) * 0.8, behavior: 'instant' });
  });
  await p.waitForTimeout(900);

  const out = [];
  for (const sel of ['.banner h1','.banner h1 em','.banner__sub','.mark']) {
    const r = await read(sel);
    if (r) out.push(r);
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
    const r = await read(sel);
    if (r) panelOut.push(r);
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
        size, weight = item["size"], item.get("weight", 400)
        # WCAG "large scale": >=24px, or >=18.66px only when bold (>=700).
        large = size >= 24 or (size >= 18.66 and weight >= 700)
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
