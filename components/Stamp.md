# Stamp

**Purpose:** a punchline badge that lands hard ("−62.5% load time", "Shipped").

**Props:** `text`, `tone`, `at`, `out`, `rotate` (default −6°).

**Look**
- A thick 4 px border in the tone color, uppercase Inter 800, letter-spacing 0.04em, on a translucent panel.
- Slightly rotated, placed over the related graphic but never over the face.

**Motion**
- Land: scale 1.6 → 1 with a stiff spring (low damping, small overshoot) plus a fade, over about 8 frames, with a stamp SFX at low volume.
- A single subtle shake (2 px, 4 frames) on impact. Never loop.
- Exit: fade over 8 frames.

**Gotchas**
- Use at most one stamp per beat, or it stops being a punchline.
- It triggers on the spoken number, not on the start of the sentence.
