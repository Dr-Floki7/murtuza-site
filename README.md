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

## Outstanding work

### 1. The hero clip

Not generated yet. The page runs on a lit gradient stage until `scrub.mp4` exists, which is a
deliberate graceful degradation, not a bug.

Follow [`HERO_CLIP_PROMPTS.md`](HERO_CLIP_PROMPTS.md). It has the three shot prompts, hard framing
specs, and the identity block from `murtaza_character_profile/`. Produce `clip1.mp4`, `clip2.mp4`,
`clip3.mp4` in this directory.

Then concatenate and re-encode:

```bash
# ffmpeg is not installed yet:  winget install Gyan.FFmpeg
printf "file 'clip1.mp4'\nfile 'clip2.mp4'\nfile 'clip3.mp4'\n" > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy joined.mp4

ffmpeg -i joined.mp4 -an -vf "scale=1280:-2,fps=30" -c:v libx264 -preset slow -crf 20 \
  -x264-params "keyint=1:min-keyint=1:scenecut=0" -movflags +faststart scrub.mp4

# social preview image, pulled from the final frame of the last stage
ffmpeg -sseof -0.5 -i scrub.mp4 -vframes 1 -vf "scale=1200:630:force_original_aspect_ratio=increase,crop=1200:630" og-cover.jpg
```

Then recalibrate against the real file: the stage bands in `panelFor()`, `object-position` on
`.act__video`, the `.act` height against real duration, and the scrim positions against where the
light actually falls.

### 2. Swap the domain placeholder

`murtuza.vercel.app` appears in `index.html` (15×), `robots.txt`, `sitemap.xml` and `llms.txt`. Replace all
of them once the real domain is known.

### 3. Wire the voice agent

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
