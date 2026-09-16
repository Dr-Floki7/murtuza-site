# murtuzabharmal.com

Personal site for Murtuza Bharmal. One self-contained `index.html` with a scroll-scrubbed video
hero. No build step, no framework, no dependencies at runtime.

Architecture and editorial decisions live in [`PRODUCT.md`](PRODUCT.md). The visual direction
contract is in `.impeccable/surfaces/index-html.md`.

## Run it

```bash
python -m http.server 8099
# then open http://127.0.0.1:8099/index.html
```

It must be served over HTTP. Opening the file directly with `file://` breaks the font load and
video seeking.

## How the hero works

A ~800vh spacer with the video pinned `position: sticky`. On scroll, progress across the spacer
maps to `progress × video.duration`, and a `requestAnimationFrame` loop eases the real
`currentTime` toward that target (lerp factor 0.12) so it reads smooth instead of jumpy. Three
copy panels cross-fade at stage boundaries.

Instant seeking requires an all-keyframe encode. A normal MP4 only seeks to keyframes, so
scrubbing a standard encode stutters badly.

`prefers-reduced-motion` skips scrubbing entirely: the clip loops quietly and all three stage
panels render as a static stack.

## Live

**https://murtuza-bharmal.vercel.app**

Verify a deploy with `python live-check.py`. It checks page *content*, not status codes: a Vercel
login wall returns 200 for every path, including files that do not exist, so status codes alone
prove nothing. That wall silently hid this site once already.

Deployment Protection must stay **disabled** for the site to be publicly reachable.

## Rebuilding the assets

Raw Flow output lives in `Videos/` and is committed on purpose — it is irreplaceable source
material. To rebuild everything the page serves:

```bash
winget install Gyan.FFmpeg     # if not already present
python build-assets.py
```

That concatenates in reverse-chronological order, encodes all-keyframe inside a 24 MB budget
(Cloudflare Pages caps single files at 25 MiB, so staying under keeps that host an option),
produces both landscape and portrait cuts, generates `banner.webp` / `banner.jpg` / `og-cover.jpg`,
and prints the stage boundaries as scroll fractions.

If clip durations change, update the bands in `panelFor()` in `index.html` to the fractions the
script prints. Current cut: real estate 0.00–8.00s, electronics 8.00–16.00s, clinical 16.00–22.04s.

Portrait viewports are served `scrub-portrait.mp4`, chosen in JS at load. Not via `<source media>`,
whose `media` attribute is evaluated only once and is unevenly supported.

## Engagement tracking

Vercel Web Analytics: cookieless, ~1KB, no consent banner required. Hobby includes 50K
events/month and pauses collection rather than billing when exceeded.

Conversions (`cv_download`, `email_click`, `linkedin_click`) fire immediately. Everything else is
batched into a single `visit_summary` event at end of visit, so a visit costs roughly two events
rather than a dozen. The summary reports which section held attention longest, total engaged time,
max scroll depth, how far into the film the visitor reached, and viewport orientation — all
bucketed, which keeps distinct-value counts low and avoids anything resembling a fingerprint.

A hidden tab does not accrue time. `pagehide` is used rather than `unload`, which would disqualify
the page from the browser's back/forward cache.

## Outstanding work

### Wire the voice agent

`#agent-mount` in `index.html` is the slot. Use a hosted provider (ElevenLabs Agents, Vapi, Retell)
with a domain-locked public embed ID.

**Never put an API key in this file.** It is a static page; anything in it is public on deploy.
Guardrails and the knowledge base belong in the provider's dashboard, server-side, where a visitor
cannot edit them.

## Checks

```bash
npm install                 # playwright, dev only
node verify.js              # widths 320→2560 + landscape phone + reduced motion
python seo-check.py         # JSON-LD parses, and every schema claim is visible on the page
```

`verify.js` drives locally installed Chrome, since the bundled Chromium download fails on this
machine. It asserts no horizontal scroll, 44px tap targets, 16px minimum body text on mobile,
that `position: sticky` survives `overflow-x: clip`, that the video covers at every ratio, that
the primary CTA is hit-testable, and that the skip link appears on focus.

The design skill's mechanical detector:

```bash
~/.kiro/skills/impeccable/scripts/impeccable.cmd detect --json index.html
```

Six `cramped-padding` findings and one `clipped-overflow-container` are known false positives:
the detector cannot resolve `clamp()` padding, inline padding comes from the `.wrap` wrapper, `.act`
is intentionally full-bleed, and `overflow-x: clip` is the specific choice that preserves sticky
(unlike `overflow: hidden`). Sticky behaviour is verified at all 11 widths by `verify.js`.

## Editorial constraints

Read `PRODUCT.md` before changing copy. The load-bearing ones:

- The current employer is never named. Its revenue figures are not published either.
- Xiaomi India is named in full, with its metrics. Past employer, no exposure.
- The phone number stays out of the page and lives only in the CV PDF.
- Nothing invented. No testimonials, case studies or client references exist to cite.
