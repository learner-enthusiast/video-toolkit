# CostMeter

**Purpose:** the recurring meter for "count vs cost": starts as a plain LCD counter, reveals a hidden needle that swings when the real cost runs away, becomes a ₹ readout per call, and settles in the recap. Same object in every scene.

**Props:** `w`, `readout` (LCD text), `caption`, `dial` (0 hides the gauge, 1 shows it; animate to reveal), `needle` (0..1, may overshoot slightly), `zone` ([from, to] orange arc, default the last quarter).

**Look**
- White panel (dark: #1A1A1A, white 60% border), brand border, radius, shadow. Gauge: half-circle warm-grey arc, orange zone, 11 ticks, near-black needle, orange pivot. LCD: #0D0D0D block, JetBrains Mono 700 orange, tabular. Caption: Inter 800 uppercase dim.

**Motion**
- Counter mode (`dial: 0`) just updates the readout. Reveal: `dial` eases 0→1 over ~10 frames, then the needle springs (damping ~9) hard right. Recap: the needle springs into the orange zone on "meter the money".

**Gotchas**
- Keep its size and type consistent across scenes so it reads as one object; place it where it never covers a scene's key element (top-left corner in a two-column compare).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
