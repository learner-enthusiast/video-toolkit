# ScreenshotKenBurns

**Purpose:** make every screenshot a living shot that moves toward what I'm talking about.

**Props:** `src`, `rect` (the screen card), `keys` (list of `{at, focus: [x, y, w, h] in image px}`), `out`.

**Do**
- Look at the image yourself and find the regions named in the cue (form fields, source list, button). Write their pixel boxes into `keys`.
- Each key frames its focus box inside the card with some padding. Move between keys with ease-in-out over 20–40 frames.
- Between keys, keep a gentle drift (1–3% zoom or pan). Nothing stays static for more than 3 s.
- Show it inside a `Card`-style frame with the brand radius and shadow.

**Gotchas**
- Never magnify past about 2x; screenshots go soft. Exceed that only if it's needed to cover the card.
- Clamp so the card is always covered. Center the image on any axis where it is smaller than the card.
- Blur personal data (other people's emails, tokens) on a working copy, never on `assets/`.
- Switch between shots with a crossfade or a short slide (8–12 frames).
