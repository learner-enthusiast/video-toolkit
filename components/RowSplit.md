# RowSplit

**Purpose:** a wide database row whose columns split between two stores (e.g. some go to a search index, the rest stay in the main database).

**Props:** `columns` (name, `dest`: "move" | "stay", `type` tag for moved ones, `lock` bool, `at`), `from` (label/logo of the source store), `to` (label/logo of the target box), `rect`, `splitAt`, `out`.

**Look**
- The row: one horizontal strip of column cells (Inter 600 names, JetBrains Mono sample values), 2 px border, brand radius, inside the source store's card with its label or logo tile.
- At phone width the 8 columns wrap to 2 rows of 4 cells, still read as one record.
- Target box: a `Card` with the target's logo tile and title.
- Type tags under moved cells (`text`, `keyword`, `number`, `id`): `Tag` pills, orange outline.
- `lock`: a small padlock line icon on the cell, which stays put and dims to warm grey.

**Motion**
- Cells pop in left to right on their spoken names, staggered 4–6 frames.
- On `splitAt`, moved cells lift and spring into the target box in order (stagger 4–6 frames); stayers stay and dim slightly.
- Type tags pop on their own words. The lock clicks in (scale + small rotate) on its word.
- Exit: fade together, or hand off to `FlowDiagram` by keeping both boxes.

**Gotchas**
- Compute cell rects in one place so moved cells start exactly where they were.
- Keep cell text ≤ 12 chars ("supplier cost" fits; use the shortest honest label).
