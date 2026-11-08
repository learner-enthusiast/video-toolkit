# LineChart

**Purpose:** a line that draws itself on simple axes (U-curve "lost in the middle"), with an annotated dip and a citation.

**Props:** `points`, `xLabel`, `yLabel`, `drawAt`, `annot` (text, `at`), `cite`, `rect`, `out`.

**Look**
- Axes near-black 2 px, ticks minimal, labels Inter 500 ~26 px; line orange 6 px; dip area shaded warm grey with a label ("blind spot") and an orange warning mark.
- Citation small dim Inter ~22 px in the corner.

**Motion**
- Axes draw, then the line draws left to right (ease-in-out ~1 s), dip label pops.

**Gotchas**
- A conceptual curve must say so (no fake axis numbers).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
