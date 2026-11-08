# KeyPicker

**Purpose:** four cards IP · User ID · API key · Phone/Device; the active one lifts and glows orange, the rest dim grey.

**Props:** `active` (index or null, with frame), `checks`, `rect` (card-local), `at`, `out`.

**Look**
- 2×2 grid of brand cards: white, 2 px border, 14 px radius.
- Line icon + label on each card, Inter 700 ≥ 48 px.
- Active: orange border, orange icon, lift −16 px + shadow.
- Others: opacity 0.45, grey.

**Motion**
- Cards pop in, staggered 5 frames.
- Activation springs.

**Gotchas**
- The same component returns for options 2–4 with a different active card; keep positions identical so it reads as one picker.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
