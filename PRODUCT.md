# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static single-file HTML/CSS/JS. Confirmed by the user after an explicit trade-off round: the
alternative (Next.js + Tailwind + shadcn, which would have unlocked the Skiper UI / Vengeance UI
component libraries named in `UI & Skills.docx`) was presented and declined in favour of the
single-file architecture specified in `My site flow.pdf`. No build step, no framework.

Assets sit next to `index.html` (the scrubbed clip, the CV PDF, self-hosted fonts). "Single file"
constrains the toolchain, not the asset folder.

Deploy target: Vercel (CLI 59.1.4 installed, authenticated as `dr-floki7`). Source of truth is a
GitHub repo under the user's account.

## Users

**Primary: recruiters, hiring managers, and talent partners** in healthcare, medtech, and
healthtech. They arrive from a LinkedIn profile or a CV, usually on a phone, usually mid-shortlist,
scanning for a reason to keep reading or to move on. Their job is to decide within seconds whether
this candidate's unusual background is an asset or a red flag.

**Secondary: prospective advisory clients** looking for GTM and launch help. Same page, lighter path,
never at the primary audience's expense.

## Product Purpose

A personal site that converts the visitor into either a conversation about a role or a CV download.
Job-hunt is the primary job; consulting enquiry is the secondary one. Success is a reply in the
inbox, not time on page.

## Positioning

A clinically trained dentist (BDS) who became a GTM lead (MBA, Marketing). The combination a
neighbouring candidate cannot truthfully copy: five-plus years of launch execution in two hardware
and high-ticket categories, sitting on top of real clinical experience with how patients actually
decide, delay, and act.

Most product marketers pitching into healthtech have the commercial half and have read about the
clinical half. This is the reverse, and the clinical half is first-hand.

## Operating Context

The visitor is almost always on a phone, often on a poor connection, and gave the page a few seconds
before deciding. They are cross-referencing against a LinkedIn tab and a CV PDF. They may be a
non-specialist recruiter screening against a keyword list, or a hiring manager reading for judgement.
The page has to serve both without pandering to either.

## Capabilities and Constraints

Confirmed content:

- Career arc across three sectors: clinical practice (2013–2020), consumer electronics
  (Xiaomi India, 2022–2025), real estate (2025–present)
- Education: MBA Marketing (Nirma University), BDS (AMC Dental College & Hospital)
- Google certifications (Digital Marketing Fundamentals, Analytics); Performance Excellence Award
  across three consecutive quarters; Head of Retail recognition for Diwali 2023

Hard editorial constraints, all user-confirmed:

- **Story over metrics.** The user explicitly redirected away from a numbers-led page toward the
  narrative: sectors, years, launches, and skills.
- **Current employer is not named.** Referred to as "an India real estate developer." A public
  job-hunt page naming the current employer announces the job hunt to them. The employer's own
  revenue figures (₹500+ Cr launch revenue, ₹30+ Cr budgets) are therefore not published as
  figures either; scope is expressed qualitatively.
- **Xiaomi India is named in full** with its metrics. Past employer, recognisable brand, ages-old
  numbers, no exposure.
- **Cut entirely:** the CRM vendor name, and the 8%→12% site revisit rate (internal ops metric,
  no external meaning).
- **Contact:** email and LinkedIn are public. Phone number is not, on a scraped-forever public
  page; it stays in the CV for people who download it. No Instagram.
- The CV PDF still names the current employer. That gap between public page and requested
  document is deliberate and functions as a soft gate.

Undecided / not yet built:

- **Name spelling is unconfirmed.** The CV header reads "Murtuza Bharmal"; the character profile
  and git identity read "Murtaza". Both are in active use. Needs one answer before launch.
- **Voice agent is deferred, not cancelled.** The user wants an agent answering questions about his
  background and refusing everything else. Architecture decided: a hosted provider (ElevenLabs
  Agents / Vapi / Retell) with a domain-locked public embed ID, so no API key ever ships in the
  static file. A slot is designed into the page; the widget is wired once the user has an account.
  Recorded caveat the user was given: "only answers about me" is not fully enforceable by prompting
  alone.

## Brand Commitments

- Name and role: GTM / Product Marketing, targeting healthcare, medtech, healthtech
- LinkedIn: `linkedin.com/in/murtaza-bharmal77/`
- Email: `dr.murtaza13b@gmail.com`
- The only volunteered visual constraint: "modern branding, not funky, AI-enabling colours."
  Recorded as given, not expanded.
- `murtaza_character_profile/` is a binding likeness specification for any generated image or video
  of the user. Identity anchors (facial structure, nose profile, beard silhouette, hairline, eye
  region, complexion) must not drift. It is a likeness spec only and deliberately infers no age,
  height, personality, or private attribute.

## Evidence on Hand

- `Murtuza_Bharmal_Resume_HT.pdf` — the factual source for all career content on the page
- `My site flow.pdf` — "The Scroll Website Guide"; the scroll-scrub engine specification the build
  follows (all-keyframe re-encode, ~500vh spacer, sticky video, lerped `currentTime`, reduced-motion
  fallback, fluid 320–2560px, per-width self-check)
- `UI & Skills.docx` — named the UI libraries and skills; libraries declined, skills adopted
- `murtaza_character_profile/` — 6 markdown files specifying the user's likeness for generation

Absences that must not be fabricated:

- **No hero clip exists yet.** The user will generate it in Google Flow from prompts I write, using
  his own reference photos. Until then the page runs on a gradient stage.
- **No photographs of the user are in the workspace.** The character profile lists what he has
  (front portraits, both profiles, full-body, blazer shots) but the image files are not here. Those
  photos are what a generation tool needs to hold the likeness; the text profile alone will not.
- No testimonials, case studies, press, or client references. None to be invented.
- No ffmpeg on the machine yet; needed for the all-keyframe re-encode once the clip exists.

## Product Principles

1. **The unusual path is the pitch.** Dentist to GTM is the most memorable thing here. Lead with it
   rather than normalising it into a generic marketing CV.
2. **Credibility without exposure.** Every claim traceable to the CV; nothing published that his
   current employer could object to.
3. **Phone-first, seconds-first.** The primary audience is scanning on mobile. Anything that only
   works at 1440px wide has failed.
4. **One conversation, two doors.** A role is the primary ask, advisory the secondary. The page never
   makes the visitor guess which door is theirs.
5. **Nothing invented.** Absences stay absent. No fabricated proof, no borrowed logos, no numbers
   that cannot be defended in an interview.

## Accessibility & Inclusion

WCAG AA as specified in `My site flow.pdf` and non-negotiable per the working agreement: semantic
landmarks, real alt text, visible focus on every interactive element, AA contrast on body and large
text, tap targets from 44×44px, no horizontal scroll at any width from 320px, body text no smaller
than ~16px on mobile, safe-area insets respected on notched phones, and `prefers-reduced-motion`
honoured by skipping the scrub entirely rather than degrading it.
