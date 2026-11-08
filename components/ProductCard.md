# ProductCard

**Purpose:** the recurring product in a running scenario (e.g. Diwali sale iPhone), so every scene reads as one story.

**Props:** `name` ("iPhone"), `logo` (official file, optional), `price` (a `PriceTag`), `accent` (diya), `clock` (text + `at`), `badge` (e.g. "1 left in stock", "Part 1"), `rect`, `at`, `out`.

**Look**
- White card on the grid, brand radius, 2 px border, soft shadow. A simple line-drawn phone silhouette (generic, no real UI), the logo on a small white tile, the name in Inter 700.
- Diya accent: a small flat oil-lamp line icon with an orange flame, top corner.
- Clock: a small pill (`12:00 AM`) in JetBrains Mono.

**Motion**
- Enters with a spring scale from 0.92 plus a fade; the flame flickers by a 1–2 px scale wobble driven by `frame` (no CSS animation).

**Gotchas**
- Same size and art in every scene it appears in; move it with a spring rather than redrawing a variant.
