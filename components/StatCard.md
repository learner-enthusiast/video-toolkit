# StatCard

**Purpose:** a stat with a before → after change and a credit ("Retrieval failures 5.7% → 1.9%").

**Props:** `label`, `before`, `after`, `credit` (logo + text), `at`, `out`.

**Look**
- White card, 2 px border; before in warm grey struck through, arrow, after big orange Inter 800 (tabular); small logo tile + credit text.

**Motion**
- Card springs up; before shows, arrow draws, after counts down to its value.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
