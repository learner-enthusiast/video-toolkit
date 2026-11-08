# ListMerge

**Purpose:** two ranked lists merge into one (Reciprocal Rank Fusion), then a counter rises to ~50.

**Props:** `lists` (items), `mergeAt`, `label`, `labelAt`, `count` (to, `at`), `rect`, `out`.

**Look**
- Two narrow columns of rank rows (JetBrains Mono rank + short label) that converge into one central column; label pill above; Counter below (`components/Counter.md`).

**Motion**
- Rows slide diagonally into interleaved slots with springs (stagger 3 frames); duplicates merge into one (scale pulse).

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
