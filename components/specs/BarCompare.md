---
code: components/code/BarCompare/BarCompare.tsx
preview: components/code/BarCompare/preview.png
props: "w, rows [{label,value,tone,at}], max"
variants: "shared scale, ink vs orange"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
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

## Code

Saved: `components/code/BarCompare/BarCompare.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: w, rows [{label,value,tone,at}], max.
- First built and rendered in `system-design-of-ai/11-max-tokens-and-truncation`.
