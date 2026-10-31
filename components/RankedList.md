# RankedList

**Purpose:** search results that reorder by relevance: the right item rises to the top, a weak match drops down.

**Props:** `query` (shown in a search pill), `items` (id, label, `score`), `orderBefore`, `orderAfter`, `at` (reorder word), `winner`, `loser`, `out`.

**Look**
- A generic search pill (brand style, no real app UI) above a stack of result rows on a `Card`: rank number in JetBrains Mono, label in Inter 600, optional small score bar.
- Winner: orange border and an orange rank number after the reorder. Loser: dims to warm grey.

**Motion**
- Rows enter in `orderBefore`, staggered 4–6 frames.
- On `at`, every row springs to its `orderAfter` slot (translateY only, ~0.4 s, slight overshoot); the winner scales 1 → 1.04 → 1 and glows, the loser sinks and dims.
- Exit: fade and lift.

**Gotchas**
- Rows have a fixed height, so positions come from the index, never measured layout.
- ≤ 5 rows at phone width; labels ≤ 22 chars.
