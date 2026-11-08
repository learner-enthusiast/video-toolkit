# Badge

**Purpose:** a stamp-like badge for a key property ("No retraining").

**Props:** `text`, `at`, `out`, `rotate` (deg, ~−6).

**Look**
- Orange fill, white Inter 800 text ~36 px, full-radius pill or rounded rectangle, 2 px #1A1A1A border, slight rotation.

**Motion**
- Stamp in: scale 1.4 → 1 with a spring, small 3 px card shake, optional stamp SFX.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
