---
code: components/code/CounterPair/CounterPair.tsx
preview: components/code/CounterPair/preview.png
props: "left {label, to, from?, at, dur?}, right {label, value, at}, w?, y?"
variants: "dark punch (default)"
last_used: Graphify
---
# CounterPair

**Purpose:** a two-number twist: one big number counts up (effort, reminders, attempts) beside a second that stays at a stark value (results, uses: 0). Dark punch style.

**Props:** `left` (label, count target, start, frame, duration), `right` (label, fixed value, frame), `w`, `y`.

**Look**
- Two dark tiles (#151515) side by side; small-caps Inter 800 labels; Inter 900 ~150 px numbers. The left number white, the right one orange with an orange border.

**Motion**
- Tiles enter with the brand rise; the left number counts with ease-out; the right number pops (scale 0.8 → 1) on its word.

## Code

Saved: `components/code/CounterPair/CounterPair.tsx` (preview: `preview.png`).
