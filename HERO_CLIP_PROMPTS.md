# Visual assets — generation brief

Two deliverables:

1. **`banner.jpg`** — one still image, three versions of you in a single frame. This is the first
   thing anyone sees. Static, so the page paints instantly.
2. **`scrub.mp4`** — three 6-second clips, concatenated, playing mid-page under scroll control.
   Reverse chronological: real estate, then electronics, then the white coat.

Built from `murtaza_character_profile/CHARACTER_BIBLE.md` and `SHOT_PROMPT_TEMPLATE.md`.

---

## Why the order is reversed

Chronological order puts the white coat first, which frames you as a dentist attempting a switch.
Reverse order puts the blazer first, which frames you as a GTM lead with an unusual edge. Same
facts, different read, and only the second one survives a six-second recruiter skim.

The coat becomes a reveal instead of a label. By the time it appears the visitor has already
read "GTM Manager."

---

## Hard specs — not stylistic, the page breaks without them

| Spec | Value | Why |
|---|---|---|
| Aspect | 16:9 | The page crops it per device |
| Clip length | 6s each, 3 clips | 18s all-keyframe lands ~40MB. Longer and mobile stalls |
| Sound | Off | Stripped in the re-encode anyway |
| Subject position | Centred, medium shot, head in the upper-middle third | A portrait phone crops the sides off entirely |
| Headroom | Space above the head | The page biases the crop upward to hold faces |
| Camera motion | Slow, continuous, one direction | Scrubbing jumps frames; fast or reversing motion stutters |
| Lower-left frame | Visually quiet and dark | All page copy sits there |
| Banner resolution | Highest available, 16:9 | Save as `banner.jpg` |

**No logos, no readable branding, no text in frame.** Unbranded handset throughout.

**Never show the coat being removed.** Wardrobe changes happen *between* clips. Each clip ends with
you moving past the lens, which hides the change and makes three clips read as one journey.

---

## Identity block — paste at the top of EVERY image prompt

> Photorealistic representation of Murtuza based on the supplied reference photos. Preserve the same
> recognizable facial structure, broad natural face, defined prominent nose and side profile, dark
> eyes, short dark textured side-swept hair, full dark beard with connected moustache and fuller chin
> volume, natural medium-brown complexion, realistic skin texture, and natural body proportions. Do
> not beautify, slim, reshape, age, de-age, or replace the face. The character must remain the same
> person as in the reference images.

Attach your reference photos every time. Text alone will not hold a face across four generations.

---

# BANNER — three of you, one frame

Static image, 16:9, highest resolution. Save as `banner.jpg`.

```
[IDENTITY BLOCK]

Three versions of the same man, identical face and identical likeness in all three,
standing in one wide dark modern interior. All three are unmistakably the same person.

CENTRE, closest to camera, sharp focus, dominant, lit brightest: he wears a dark navy
blazer over a light blue button-down shirt, standing squarely and looking directly into
the lens, composed and confident, hands relaxed at his sides. He is the primary subject.

LEFT, one step further back, slightly softer focus, dimmer: the same man in a white
clinical coat over a light shirt, standing in three-quarter profile, looking down and
away toward the left, calm and thoughtful.

RIGHT, one step further back, slightly softer focus, dimmer: the same man in a
well-fitted dark casual polo shirt, holding a completely unbranded modern smartphone at
chest height, glancing down at its screen.

Wide cinematic composition. All three figures occupy the upper two thirds of the frame.
The floor and lower third of the frame fall away into deep shadow and empty negative
space. Cool directional key light from the front and above on the centre figure, with the
flanking figures falling off into cooler shadow. Deep near-black background with subtle
architectural depth. Ultra photoreal, natural skin texture, realistic hair and beard,
35mm feel, cinematic contrast and colour grade, no text, no logos, no watermark, no
branding, no visible phone branding, 16:9.
```

Two things to watch. The centre figure must be sharpest and brightest — that hierarchy is what
makes corporate the first impression rather than a three-way tie. And check all three faces against
`IDENTITY_LOCK.md` separately; the flanking figures are where drift hides.

If three clean clones do not land after several attempts, fall back to a single corporate portrait:
the centre-figure description alone, full frame. The page works either way.

---

# CLIP 1 — Real estate (opens the film)

### Start frame
```
[IDENTITY BLOCK]

A dim architectural studio at night. On a table in the foreground sits a large, precisely
built, internally lit scale model of a modern residential development, glowing warm
against the dark room. He wears a dark navy blazer over a light blue button-down shirt.
Medium shot, centred, leaning slightly over the model and studying it, thoughtful and
absorbed. The model's warm glow is the key light on his face from below and in front; the
room falls away to deep shadow. Lower left of the frame is dark and empty. Ultra
photoreal, natural skin texture, 50mm feel, cinematic contrast, no text, no logos, no
watermark, wide 16:9 composition.
```

### End frame
```
[IDENTITY BLOCK]

The same dim architectural studio, same glowing scale model, same dark navy blazer and
light blue shirt, continuous art direction. He has straightened up from the model and is
stepping forward toward the lens, looking directly into camera, composed and confident.
Closer than the start frame, still centred. Same warm model glow as the key light, deep
shadow behind. Lower left dark and empty. Ultra photoreal, natural skin texture, 50mm
feel, cinematic contrast, no text, no logos, no watermark, wide 16:9 composition.
```

### Motion line
```
Slow continuous cinematic arc drifting around the glowing architectural model as he
straightens up from studying it, turns to the lens and steps forward past camera. Single
smooth camera move, warm light from the model raking across his face, no cuts, confident
and deliberate.
```

---

# CLIP 2 — Consumer electronics

Feed **clip 1's end frame** as an identity ingredient alongside your reference photos.

### Start frame
```
[IDENTITY BLOCK]

A modern consumer electronics retail interior, bright and warm, softly out of focus
behind him. He wears a well-fitted dark casual polo shirt. Medium shot, centred, head and
shoulders in the upper-middle third. He holds an unbranded modern smartphone at chest
height and is looking at its screen, focused and confident. Clean retail shelving and
warm display lighting bokeh behind him. Warm key light from the front left. Lower left of
the frame uncluttered and darker. Ultra photoreal, natural skin texture, 85mm feel,
shallow depth of field, completely unbranded devices, no text, no logos, no watermark,
wide 16:9 composition.
```

### End frame
```
[IDENTITY BLOCK]

The same retail interior, same warm lighting, same dark casual polo, continuous art
direction. He has lowered the unbranded smartphone to his side and is stepping forward
toward the lens, gaze lifting past camera, a slight confident half-smile. Closer than the
start frame, still centred. Same warm retail bokeh behind him, lower left still darker
and uncluttered. Ultra photoreal, natural skin texture, 85mm feel, unbranded devices, no
text, no logos, no watermark, wide 16:9 composition.
```

### Motion line
```
Smooth continuous camera move drifting forward as he lowers the phone, lifts his gaze and
steps past the lens. Single-direction motion, warm retail lights sliding through soft
bokeh behind him, no cuts, confident and unhurried.
```

---

# CLIP 3 — Clinical (the reveal, closes the film)

Feed **clip 2's end frame** as an identity ingredient alongside your reference photos.

### Start frame
```
[IDENTITY BLOCK]

A modern dental clinic in cool daylight. He wears a white clinical coat over a light
shirt. Medium shot, standing beside a dental operatory chair, head and shoulders in the
upper-middle third, centred. He is looking down at a patient chart in his hands, calm and
focused. Clean clinical surfaces, stainless instruments softly out of focus behind him.
Cool white overhead light as the key, shadows falling off to the sides. Lower left of the
frame uncluttered and dim. Ultra photoreal, natural skin texture, 85mm feel, shallow
depth of field, no text, no logos, no watermark, wide 16:9 composition.
```

### End frame
```
[IDENTITY BLOCK]

The same dental clinic, same cool daylight, same white clinical coat, continuous art
direction. He has lowered the chart and turned to face the camera directly, still and
composed, holding the look. Slightly closer than the start frame, centred, calm neutral
expression. Same clinical surfaces behind him, same cool white key light, lower left
still dim and uncluttered. Ultra photoreal, natural skin texture, 85mm feel, no text, no
logos, no watermark, wide 16:9 composition.
```

### Motion line
```
Slow continuous cinematic push-in as he lowers the chart and turns to face the lens,
settling and holding on him. Smooth single-direction camera move, subtle parallax on the
clinic behind him, no cuts, calm and final.
```

---

## Negative prompt — every generation

```
Different person, different people, three different men, inconsistent faces, face
variation between figures, generic model, altered face, slimmed face, narrow nose,
different nose profile, different beard, clean-shaven, different haircut, excessive
beauty filter, plastic skin, over-smoothed skin, altered eye color, exaggerated jawline,
distorted anatomy, unrealistic hands, extra fingers, extra limbs, merged bodies,
duplicate person, face melting, asymmetrical eyes, artificial teeth, unrequested glasses,
hat, tattoos, scars, piercings, text, watermark, logo, brand name, visible phone
branding, subtitles, captions, letterboxing, fast camera movement, jump cuts, strobing,
cluttered lower third, busy floor.
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

If a clip lands at 5 or 8 seconds instead of 6, that is fine. I recalibrate the stage timings
against whatever the real durations turn out to be. Do not force it.

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
slightly different man is the one failure mode this approach cannot survive.

---

## Deliver

- `banner.jpg` in the project root
- `clip1.mp4`, `clip2.mp4`, `clip3.mp4` in the project root

Then I concatenate, re-encode to all-keyframe so scrubbing is instant, pull the social preview image,
and calibrate the page: stage timings against real timestamps, `object-position` against your actual
framing, act height against real duration, and the copy scrims against where the light actually falls.
