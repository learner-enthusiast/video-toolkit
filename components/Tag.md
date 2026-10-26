# Tag

**Purpose:** a small pill or chip for keywords, topics, verbs ("Summarize", "Draft reply") and icon-less tech names.

**Props:** `label`, `at`, `out`, `tone` (accent | good | bad | neutral), `mono`, `size`.

**Look**
- Pill shape (full radius), a tinted background at about 15% of the tone color, and a 1 px border in the tone color at about 50%.
- Inter 600 at about 28 px, or JetBrains Mono when `mono`.
- Green and red tones only for good/bad meaning, per `brand.md`.

**Motion**
- Pop: a spring scale 0.8 → 1 with a slight overshoot, plus a fade. An optional soft pop SFX at low volume.
- In a group, stagger by 4–6 frames, each one triggered on its own spoken word if possible.
- Exit: fade and scale to 0.95.

**Gotchas**
- Keep tags on a row grid. Measure text width so a row never overflows the free area.
- No emojis inside tags.
