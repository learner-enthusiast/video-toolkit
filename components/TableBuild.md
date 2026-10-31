# TableBuild

**Purpose:** a database table that assembles cell by cell, to show "data in rows and columns".

**Props:** `columns` (names), `rows` (cell values), `rect`, `at` (first cell), `cellStagger` (frames, default 2), `title`, `tags` (label, `at`), `out`.

**Look**
- Header row on a near-black block with white Inter Medium; body cells on white with 1 px grid-line borders, the whole table inside a 2 px border with the brand radius.
- Values in Inter Regular (JetBrains Mono for ids and numbers).
- Optional `title` (the table name) in the headline font above it.

**Motion**
- Header cells pop left to right, then body cells row by row with a spring scale 0.85 → 1 and fade, staggered by `cellStagger`.
- "rows" and "columns" can each get a brief accent highlight sweep on their spoken word.
- `tags` (e.g. PostgreSQL, MySQL) pop in below as `Tag`s on their words.
- Exit: fade together, or hand off to `TableJoin` by keeping the table on screen.

**Gotchas**
- Keep it ≤ 4 columns × 4 rows at phone width; cell text ≤ 10 chars.
- Total build must finish before the next idea starts; shrink the stagger if the line is short.
