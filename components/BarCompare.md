# BarCompare

**Purpose:** before/after comparison ("4.0s → 1.5s", "full table scan vs. indexed lookup").

**Props:** `rows` (label, value, tone, `at`), `max`, `unit`, `out`, `mode` (side-by-side | shrink).

**Look**
- Horizontal bars, 28–36 px tall, with radius 8, on a faint track.
- The before bar is red and the after bar green. Labels in JetBrains Mono on the left, values in Inter 700 at the bar end.

**Motion**
- Side-by-side: each bar grows from 0 to its value with an ease-out (about 18 frames) on its word, staggered.
- Shrink mode: a single bar starts at the before value in red, then shrinks to the after value while the color crossfades to green, and the value label counts.
- Exit with a fade.

**Gotchas**
- Scale bars to a shared max so the comparison is honest.
- Pair it with `Stamp` for the punchline (e.g. "−62.5% load time").
