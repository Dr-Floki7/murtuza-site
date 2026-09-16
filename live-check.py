"""Verify the deployed site is genuinely public and serving the real page.

    python live-check.py [url]

Checks page content, not status codes. A Vercel login wall returns 200 for every
path including files that do not exist, so status codes alone prove nothing.
"""
import sys, urllib.request, urllib.error, re

sys.stdout.reconfigure(encoding="utf8")
BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://murtuza-bharmal.vercel.app").rstrip("/")
UA = {"User-Agent": "Mozilla/5.0 (compatible; deploy-check)"}
fails = []


def fetch(path, headers=None):
    h = dict(UA)
    if headers:
        h.update(headers)
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=h), timeout=45) as r:
            return r.status, dict(r.headers), r.read(), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), b"", BASE + path
    except Exception as e:
        return None, {}, str(e).encode(), BASE + path


# ── is it public at all? ──────────────────────────────────────────────
st, h, body, final = fetch("/")
html = body.decode("utf8", "replace")
walled = "vercel.com/login" in final or "sso-api" in final
print(f"GET /  -> {st}   {len(body)/1024:.1f} KB")
print(f"  landed on: {final}")
if walled:
    fails.append("STILL BEHIND THE VERCEL LOGIN WALL")
    print("  FAIL: redirected to a Vercel login page")
else:
    print("  ok: no auth redirect")

print("\nis this the real page?")
for label, probe in (
    ("headline", "Three industries"),
    ("banner element", 'class="banner__img"'),
    ("banner poster", 'poster="banner.jpg"'),
    ("JSON-LD", "application/ld+json"),
    ("Person schema", '"jobTitle"'),
    ("Flow Realty named", "Flow Realty"),
    ("six film beats", 'data-panel="5"'),
    ("ticker", 'class="ticker'),
    ("agent dialog", 'id="agent-dialog"'),
    ("analytics", "_vercel/insights"),
    ("instrumentation", "visit_summary"),
):
    ok = probe in html
    print(f"  {'ok ' if ok else 'FAIL'} {label}")
    if not ok:
        fails.append(f"missing from live html: {label}")

canon = re.search(r'rel="canonical" href="([^"]+)"', html)
print(f"  canonical: {canon.group(1) if canon else 'MISSING'}")
if not canon or "murtuza-bharmal.vercel.app" not in canon.group(1):
    fails.append("canonical wrong")

# ── assets ───────────────────────────────────────────────────────────
print("\nassets")
LARGE = {"/scrub.mp4", "/scrub-portrait.mp4", "/banner.mp4", "/banner-portrait.mp4"}

for p, want_type in (
    ("/scrub.mp4", "video/mp4"),
    ("/scrub-portrait.mp4", "video/mp4"),
    ("/banner.webp", "image/webp"),
    ("/banner.jpg", "image/jpeg"),
    ("/og-cover.jpg", "image/jpeg"),
    ("/fonts/archivo-var.woff2", "font/woff2"),
    ("/Murtuza_Bharmal_Resume_HT.pdf", "application/pdf"),
    ("/robots.txt", "text/plain"),
    ("/sitemap.xml", "xml"),
    ("/llms.txt", "text/plain"),
):
    # Large media: ask for the first KB only. A full GET of 10+ MB can outrun the
    # timeout and read as a failure when the file is perfectly healthy.
    ranged = p in LARGE
    st, h, body, _ = fetch(p, {"Range": "bytes=0-999"} if ranged else None)
    ctype = h.get("Content-Type", "")
    ok = st in ((206, 200) if ranged else (200,)) and want_type in ctype

    if ranged and h.get("Content-Range"):
        total = h["Content-Range"].split("/")[-1]
        mb = f"{int(total)/1024/1024:.2f} MB" if total.isdigit() else "?"
    else:
        size = h.get("Content-Length", "?")
        mb = f"{int(size)/1024/1024:.2f} MB" if size.isdigit() else "?"

    print(f"  {'ok ' if ok else 'FAIL'} {st}  {mb:>9}  {ctype[:28]:<28} {p}"
          f"{'  (ranged)' if ranged else ''}")
    if not ok:
        fails.append(f"{p} -> {st} {ctype}")

# ── the thing scrubbing depends on ───────────────────────────────────
print("\nrange requests (scrubbing needs these)")
st, h, body, _ = fetch("/scrub.mp4", {"Range": "bytes=1000-1999"})
cr, ar = h.get("Content-Range"), h.get("Accept-Ranges")
ok = st == 206 and cr
print(f"  {'ok ' if ok else 'FAIL'} status {st} (want 206)  Content-Range {cr}  Accept-Ranges {ar}")
if not ok:
    fails.append("server does not honour Range requests; scrubbing will not work")

# ── caching + security ───────────────────────────────────────────────
print("\ncaching")
for p in ("/", "/scrub.mp4", "/banner.jpg", "/fonts/archivo-var.woff2"):
    _, h, _, _ = fetch(p)
    print(f"  {h.get('Cache-Control','-')[:46]:<46} {p}")

print("\nsecurity headers")
_, h, _, _ = fetch("/")
for k in ("X-Content-Type-Options", "Referrer-Policy", "X-Frame-Options",
          "Strict-Transport-Security", "Permissions-Policy"):
    v = h.get(k)
    print(f"  {'ok ' if v else 'warn'} {k}: {v}")

print()
if fails:
    print("FAILURES")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"LIVE AND PUBLIC: {BASE}")
