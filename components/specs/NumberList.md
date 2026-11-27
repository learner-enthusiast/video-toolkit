---
code: components/code/brand3/NumberList/NumberList.tsx
preview: components/code/brand3/NumberList/preview.png
props: "items, litAt, cols, w, at, out"
variants: "1 or more columns"
last_used: "—"
---
# NumberList

**Purpose:** a numbered set of terms covered one by one.

**Props:** `items`, `litAt` (frames), `cols`, `w`, `at`, `out`.

**Look**
- Numbered cards, filled column by column; number in gradient mono (`accent` to `gradientEnd`), term in Inter 700.
- Unlit cards are dim; a lit card gets an accent border and glow.

**Motion**
- Cards enter 4 frames apart; each lights on its spoken word with a small bump.
- Exit: fade over 8 frames.

**Gotchas**
- More than 10 items needs a smaller `w` check at phone size.
- Terms are the keys: keep them unique.

## Code

Saved: `components/code/brand3/NumberList/NumberList.tsx` (preview: `preview.png`, rendered in Brand 3). A Brand 3 signature piece: import `shared/brand3/NumberList/NumberList`. If another brand needs it, move its folder up to the shared library, next to the other shared components; never copy. Brand values come from `components/code/theme.ts`.

- Code props: items, litAt, cols, w, at, out.
- New for the three-brand setup; not yet used in a finished video.
