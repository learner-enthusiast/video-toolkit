# FlowArrow

**Purpose:** an arrow between two blocks that draws itself, optionally labelled ("facts"), with an orange packet travelling along it.

**Props:** `from`, `to` (points or rect anchors), `label`, `curve`, `tone`, `at`, `packet` (bool), `out`.

**Look**
- 4 px stroke, rounded caps, orange when accent, near-black otherwise; filled triangular head.
- Label pill on the midpoint (Inter 600 ~28 px).

**Motion**
- Stroke-dashoffset draw over ~12 frames (ease-in-out); head pops at the end; packets loop along the path every ~20 frames.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
