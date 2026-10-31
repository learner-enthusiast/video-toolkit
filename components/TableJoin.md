# TableJoin

**Purpose:** show a JOIN: two tables slide together, matching keys link, and a merged result appears.

**Props:** `left` and `right` (title, columns, rows), `key` (left column ↔ right column), `matches` (row index pairs), `result` (columns, rows), `rect`, `at`, `linkAt`, `resultAt`, `out`.

**Look**
- Two small tables in `TableBuild` style, side by side; titles (`users`, `orders`) in the headline font.
- Link lines: 2.5 px accent curves from a left key cell to its matching right key cell, with small accent dots at both ends; matched cells get an accent outline.
- Result table below, header in near-black, with the joined columns.

**Motion**
- `at`: both tables slide in from opposite sides with a spring and meet with a gap.
- `linkAt`: each link draws (stroke) in turn, staggered 4–6 frames, ease-in-out.
- `resultAt`: the matched rows fly down (spring) into the result table, row by row.
- Exit: fade together before `out`.

**Gotchas**
- Compute link endpoints from the cell rects, never hard-coded.
- Keep 3 rows per table and short values so it reads at phone width.
