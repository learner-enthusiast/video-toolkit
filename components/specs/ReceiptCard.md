---
code: components/code/brand2/ReceiptCard/ReceiptCard.tsx
preview: components/code/brand2/ReceiptCard/preview.png
props: "title, rows [{label,value}], alertRow {row,value,at}, at, out, w"
variants: "plain · with a row flipping to alert"
last_used: "—"
---
# ReceiptCard

**Purpose:** a cost or event tally where one line turns out wrong.

**Props:** `title`, `rows` (label, value), `alertRow` (row index, new value, frame), `at`, `out`, `w`.

**Look**
- A torn-edge receipt on `paper`, JetBrains Mono, dotted leaders between label and value.
- The flipped row turns `alert`.

**Motion**
- Rows appear 5 frames apart; the flipped value pops on its frame.
- Exit: fade over 8 frames.

**Gotchas**
- Use the flip only for a failure, never as a good/bad pair.
- Labels are one line: keep label + value under about 28 characters at the default width.

## Code

Saved: `components/code/brand2/ReceiptCard/ReceiptCard.tsx` (preview: `preview.png`, rendered in Brand 2). A Brand 2 signature piece: import `shared/brand2/ReceiptCard/ReceiptCard`. If another brand needs it, move its folder up to the shared library, next to the other shared components; never copy. Brand values come from `components/code/theme.ts`.

- Code props: title, rows [{label,value}], alertRow {row,value,at}, at, out, w.
- New for the three-brand setup; not yet used in a finished video.
