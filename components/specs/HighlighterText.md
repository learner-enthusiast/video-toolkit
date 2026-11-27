---
code: components/code/brand2/HighlighterText/HighlighterText.tsx
preview: components/code/brand2/HighlighterText/preview.png
props: "lines, marks [{word, at}], size, at"
variants: "one or many marks"
last_used: "—"
---
# HighlighterText

**Purpose:** read a sentence and underline the words that carry it.

**Props:** `lines`, `marks` (word + frame), `size`, `at`.

**Look**
- Inter 800 lines in the text colour; a marked word sits on an `accent2` block with `onAccent` text.

**Motion**
- Lines enter staggered; each marker sweeps left to right over 10 frames on its word.

**Gotchas**
- A mark matches whole words (case and punctuation ignored), each taking the first unmarked occurrence.
- Break lines yourself; they never wrap.

## Code

Saved: `components/code/brand2/HighlighterText/HighlighterText.tsx` (preview: `preview.png`, rendered in Brand 2). A Brand 2 signature piece: import `shared/brand2/HighlighterText/HighlighterText`. If another brand needs it, move its folder up to the shared library, next to the other shared components; never copy. Brand values come from `components/code/theme.ts`.

- Code props: lines, marks [{word, at}], size, at.
- New for the three-brand setup; not yet used in a finished video.
