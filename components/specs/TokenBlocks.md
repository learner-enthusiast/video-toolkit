---
code: components/code/TokenBlocks/TokenBlocks.tsx
preview: components/code/TokenBlocks/preview.png
props: "pieces [{text, byte?}], at, stagger, out, size, font (latin|deva|bengali), w, label, counter (ink|orange|false), highlight[], tone, charCount {value, at}, countLabel, charLabel, gap; also exports Block"
variants: "single row, stacked rows (EN vs Indic), one word per row"
last_used: system-design-of-ai/12-tokenizers
---
# TokenBlocks

**Purpose:** show a string as the row of tokens a real tokenizer produces, so "more blocks = more money" is learned once and reused all video. Every block on screen is the same rounded block.

**Props:** `pieces` (decoded pieces from real tokenizer JSON, e.g. `work/data/tokens.json` → `strings.h1_hi.llama3.pieces`; never hand-split), `label` (row label, e.g. "English" / "Hindi", or a logo slot), `counter` (show a running token count; `true` or `{tone:'ink'|'orange'}`), `dropStagger` (frames between blocks, default 3), `highlight` (indices drawn orange, e.g. the single "Friday" block), `byteStyle` (`'grey'` default: a piece that decodes to U+FFFD is a small grey byte block with no glyph), `charCount` (`{value, at}` dim-grey "57 chars" line under the row), `font` (`'latin'|'devanagari'|'bengali'`: Inter / Noto Sans Devanagari / Noto Sans Bengali), `w`, `at` (frame blocks start), `out`.

**Look**
- Blocks: white fill, 2 px `#1A1A1A` border, 14 px radius, padding 6×12, text at ≥ 34 px (Indic ≥ 38 px so conjuncts like "क्र", "ष्ट" stay intact). Leading spaces show as a thin dim "·" at the block's left edge.
- Highlighted block: orange fill, white text. Byte block: 60% width, `#DCD8D0` fill, dim border, no text.
- Blocks wrap onto as many lines as the width needs; rows stay left-aligned.
- Counter: Inter 900 tabular number + "tokens", right of the label; orange tone for the costly row.

**Motion**
- Blocks drop like coins: from −40 px with a spring (slight overshoot), stagger `dropStagger`; counter increments as each block lands (never linear).
- Exit: blocks fade + rise 12 px with a 1-frame stagger.

**Sound:** one soft tick (`typing-tick`, −10 dB) per landing block, thinned to every 2nd block when the stagger is < 3 frames.

**Gotchas**
- Pieces are decoded token by token; a vowel sign at the start of a piece renders with a dotted circle in some fonts. That is honest output; keep it.
- Counts must equal the tokenizer's count (`pieces.length`) and `work/facts.md`.

## Code

Saved: `components/code/TokenBlocks/TokenBlocks.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values and the Noto Sans Devanagari/Bengali fonts come from `components/code/theme.ts`.

- First built and rendered in `system-design-of-ai/12-tokenizers`.
