# Hero clip — generation brief

Three clips, 6 seconds each, 18 seconds total. They concatenate into one file that gets
scroll-scrubbed on the site. Built from `murtaza_character_profile/CHARACTER_BIBLE.md` and
`SHOT_PROMPT_TEMPLATE.md`.

---

## Hard specs — these are not stylistic, the page breaks without them

| Spec | Value | Why |
|---|---|---|
| Aspect | 16:9 | Source PDF spec; the page crops it per device |
| Length | 6s per clip, 3 clips | 18s all-keyframe lands ~40MB. Longer and mobile stalls before scrubbing works |
| Sound | Off | Audio is stripped in the re-encode anyway |
| Subject position | Centred, medium shot, head in the upper-middle third | A portrait phone crops the sides off entirely. Off-centre framing loses you |
| Headroom | Keep space above the head | The page biases the crop upward to hold the face |
| Camera motion | Slow and continuous, one direction | Scrubbing jumps frames non-linearly. Fast or reversing motion reads as stutter |
| Lower-left frame | Keep it visually quiet | All the page copy sits there. A busy or bright lower left makes text unreadable |
| Ending | Looking directly into the lens | That is the frame the call-to-action lands on |

**No logos, no readable branding, no text anywhere in frame.** Unbranded handset. Generators mangle
logos into artefacts, and a recognisable competitor device on your own site is a question you do not
need to answer.

**Never show the coat being removed.** The wardrobe changes *between* clips, never inside one. Cloth
plus hands plus a garment crossing your face is the worst-case shot for identity drift, and
`IDENTITY_LOCK.md` flags every part of it.

---

## The transition device

Each clip ends with you moving toward and past the lens; the next begins with you already in the new
setting. The subject wipes the frame, which hides the wardrobe and location change completely. Three
clips then read as one continuous journey rather than three cuts.

Do not skip this. Hard cuts between wardrobes look like three different shoots, which is exactly the
identity drift the character profile exists to prevent.

---

## Identity block — paste at the top of EVERY image prompt

> Photorealistic representation of Murtaza based on the supplied reference photos. Preserve the same
> recognizable facial structure, broad natural face, defined prominent nose and side profile, dark
> eyes, short dark textured side-swept hair, full dark beard with connected moustache and fuller chin
> volume, natural medium-brown complexion, realistic skin texture, and natural body proportions. Do
> not beautify, slim, reshape, age, de-age, or replace the face. The character must remain the same
> person as in the reference images.

Attach your actual reference photos as image references every time. The text alone will not hold a
face across three clips — the photos are what does the work.

---

## CLIP 1 — Clinical

### Start frame
```
[IDENTITY BLOCK]

A modern dental clinic in cool daylight. He wears a white clinical coat over a light
shirt. Medium shot, standing beside a dental operatory chair, head and shoulders in the
upper-middle third of the frame, centred. He is looking down at a patient chart in his
hands, calm and focused. Clean clinical surfaces, stainless instruments softly out of
focus behind him. Cool white overhead light as the key, shadows falling off to the sides.
Lower left of the frame is uncluttered and dim. Ultra photoreal, natural skin texture,
85mm feel, shallow depth of field, no text, no logos, no watermark, wide 16:9 composition.
```

### End frame
```
[IDENTITY BLOCK]

The same dental clinic, same cool daylight, same white clinical coat, continuous art
direction. He has lowered the chart and turned to face the camera directly, beginning to
step forward toward the lens. Slightly closer than the start frame. Centred, calm neutral
expression. Same clinical surfaces behind him, same cool white key light, lower left still
dim and uncluttered. Ultra photoreal, natural skin texture, 85mm feel, no text, no logos,
no watermark, wide 16:9 composition.
```

### Motion line
```
Slow continuous cinematic push-in as he lowers the chart, turns to face the lens and
steps forward toward camera, ending with him close to the lens. Smooth single-direction
camera move, subtle parallax on the clinic behind him, no cuts, calm and deliberate.
```

---

## CLIP 2 — Consumer electronics

Feed **Clip 1's end frame** as an identity ingredient alongside your reference photos.

### Start frame
```
[IDENTITY BLOCK]

A modern consumer electronics retail interior, bright and warm, softly out of focus
behind him. No clinical coat: he wears a well-fitted dark casual polo shirt. Medium shot,
centred, head and shoulders in the upper-middle third. He holds an unbranded modern
smartphone at chest height and is looking at its screen, focused and confident. Clean
retail shelving and warm display lighting bokeh behind him. Warm key light from the front
left. Lower left of the frame uncluttered and darker. Ultra photoreal, natural skin
texture, 85mm feel, shallow depth of field, completely unbranded devices, no text, no
logos, no watermark, wide 16:9 composition.
```

### End frame
```
[IDENTITY BLOCK]

The same retail interior, same warm lighting, same dark casual polo, continuous art
direction. He has lowered the unbranded smartphone to his side toward his trouser pocket
and lifted his gaze up past the camera, a slight confident half-smile. Slightly closer
than the start frame, still centred. Same warm retail bokeh behind him, lower left still
darker and uncluttered. Ultra photoreal, natural skin texture, 85mm feel, unbranded
devices, no text, no logos, no watermark, wide 16:9 composition.
```

### Motion line
```
Smooth continuous camera move drifting forward as he lowers the phone toward his pocket,
lifts his gaze and steps past the lens. Single-direction motion, warm retail lights
sliding through soft bokeh behind him, no cuts, confident and unhurried.
```

---

## CLIP 3 — Real estate

Feed **Clip 2's end frame** as an identity ingredient alongside your reference photos.
This clip ends on the frame the call-to-action sits over, so the last frame matters most.

### Start frame
```
[IDENTITY BLOCK]

A dim architectural studio at night. On a table in the foreground sits a large, precisely
built, internally lit scale model of a modern residential development, glowing warm
against the dark room. He wears a dark navy blazer over a light blue button-down shirt.
Medium shot, centred, leaning slightly over the model and studying it, thoughtful and
absorbed. The model's warm glow is the key light on his face from below and in front;
the room falls away to deep shadow. Lower left of the frame is dark and empty. Ultra
photoreal, natural skin texture, 50mm feel, cinematic contrast, no text, no logos, no
watermark, wide 16:9 composition.
```

### End frame
```
[IDENTITY BLOCK]

The same dim architectural studio, same glowing scale model in the foreground, same dark
navy blazer and light blue shirt, continuous art direction. He has straightened up and is
now looking directly into the lens, composed and confident, a faint assured expression.
Head and shoulders centred in the upper-middle third, the lit model glowing in the lower
foreground. Same warm model glow as the key light, deep shadow behind. Lower left dark
and empty. Ultra photoreal, natural skin texture, 50mm feel, cinematic contrast, no text,
no logos, no watermark, wide 16:9 composition.
```

### Motion line
```
Slow continuous cinematic arc drifting around the glowing architectural model as he
straightens up from studying it and turns to look directly into the lens, settling and
holding on him. Single smooth camera move, warm light from the model raking across his
face, no cuts, confident and final.
```

---

## Negative prompt — every generation

```
Different person, generic model, altered face, slimmed face, narrow nose, different nose
profile, different beard, clean-shaven, different haircut, excessive beauty filter,
plastic skin, over-smoothed skin, altered eye color, exaggerated jawline, distorted
anatomy, unrealistic hands, extra fingers, duplicate person, face melting, asymmetrical
eyes, artificial teeth, unrequested glasses, hat, tattoos, scars, piercings, text,
watermark, logo, brand name, visible phone branding, subtitles, captions, letterboxing,
fast camera movement, jump cuts, strobing.
```

---

## Google Flow steps, per clip

1. Generate the start image from the prompt above, 16:9
2. Generate the end image from the prompt above, 16:9
3. In Flow, add **both images as ingredients** — not as a locked end frame
4. Choose **Omni Flash**
5. Paste the motion line as the prompt
6. Generate at 6 seconds
7. If the face drifts, add the previous clip's end image plus your reference photos as extra
   ingredients and regenerate

---

## Check every output against IDENTITY_LOCK before accepting it

1. Does the face look like you?
2. Is the nose profile preserved?
3. Is the beard silhouette correct?
4. Is the hairline and hairstyle consistent?
5. Are the eyes and eyebrows recognisable?
6. Has the face been beautified or slimmed?
7. Has it quietly become a different person?
8. Hands: correct number of fingers, no deformation?
9. Any text, logo or branding that crept in?

A clip that fails on identity gets regenerated, not accepted. Three clips that each look like a
slightly different man is the one failure mode this whole approach cannot survive.

---

## Deliver

Drop the three files in the project root as `clip1.mp4`, `clip2.mp4`, `clip3.mp4`.

I concatenate them, re-encode to all-keyframe so scrubbing is instant, then calibrate the page:
stage timings against real timestamps, `object-position` against your actual framing, scroll length
against real duration, and the copy scrims against where the light actually falls.
