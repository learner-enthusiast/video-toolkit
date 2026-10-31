# InvertedIndexBuild

**Purpose:** the key visual for "inverted index": product names on sticky notes break into words, and each word lands in an index table with the product numbers stacking next to it.

**Props:** `docs` (id, text, `at`), `terms` (word order for the table), `rect`, `highlight` (term + `at`, e.g. "pro"), `jump` (term + `at`, an arrow that jumps straight to its row), `out`.

**Look**
- Sticky notes: square-ish off-white `#FFFFFF` cards with the 2 px border, brand radius, a small number badge (product id) in JetBrains Mono, text in Inter 600. Slight seeded rotation (±2°).
- Index table: two columns, "word" (Inter 600 chip) and "products" (a row of small numbered chips in JetBrains Mono).
- Highlighted row: orange block behind the word, the id chips in orange outline.
- Jump arrow: orange, drawn straight from a search pill to the row (no scanning).

**Motion**
- Notes drop in with a spring, staggered on their spoken words.
- Each note's words peel off as chips (lowercased, e.g. "iPhone" → "iphone") and fly along a gentle arc to their row, staggered 4–6 frames; a new row is created when a word is first seen.
- When a chip lands, the note's id chip appends to that row's list with a small spring bump.
- `highlight`: an orange wash sweeps across the row once. `jump`: the arrow draws in ~10 frames, the row pulses once.
- Exit: notes fade first, then the table.

**Gotchas**
- Order rows by first appearance so the build reads top to bottom.
- Keep ≤ 6 rows and ≤ 3 notes at phone width; the flight paths must not cross the caption strip.
- Lowercasing is the point (it's what the analyzer does); show it, don't hide it.
