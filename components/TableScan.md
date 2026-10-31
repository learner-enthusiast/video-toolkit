# TableScan

**Purpose:** show a full table scan: a scanner checks every row one by one while a row counter and a stopwatch run, so "slow" is felt, not stated.

**Props:** `rows` (visible row labels), `rect`, `at` (sweep start), `to` (counter end value, e.g. 10,000,000), `budgetMs` (e.g. 50), `result` (e.g. "0 results", `at`), `out`.

**Look**
- A `TableBuild`-style table (header block, white body, 1 px grid lines, 2 px border, brand radius), 6–8 visible rows of product names.
- Scanner: a 4 px orange bar across the table with a soft orange wash on the row under it; checked rows dim to warm grey.
- Counter in Inter 800 tabular figures ("rows checked"), stopwatch as a ring plus "ms" readout in JetBrains Mono.
- Over budget: the stopwatch ring and readout dim to warm grey and an orange warning mark lands next to it (brand: no red).
- `result` lands as a `Stamp`-like badge with a crossed mark, warm grey + orange border.

**Motion**
- Rows pop in staggered 4–6 frames, then the scanner sweeps down on `at` and loops faster each pass (eased, never linear) so it reads as millions.
- Counter counts with an ease-in (accelerating) curve to `to`; the stopwatch passes `budgetMs` on the word that says it's too slow.
- Exit: fade and lift together.

**Gotchas**
- At phone width keep ≤ 3 columns, cell text ≤ 14 chars.
- The counter's final value must match what I say or show (`Counter.md`).
