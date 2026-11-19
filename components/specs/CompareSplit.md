# CompareSplit

**Purpose:** side-by-side comparison of two retrieval methods (Vectors vs BM25) with good/weak examples.

**Props:** `left`, `right` (title, rows: text, tone, `at`), `rect`, `out`.

**Look**
- Two half-width cards with titles; rows show matches ("send back" ≈ "return" in orange), a weak case dimmed grey with an orange warning mark (S24/S23 dots overlapping).

**Motion**
- Rows enter on their words; the overlapping dots slide into each other on the weak case.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
