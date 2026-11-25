---
code: components/code/TokenDictionary/TokenDictionary.tsx
preview: components/code/TokenDictionary/preview.png
props: "entries[], ids[], words [{text, found, pieces, font?}], at, entriesAt, lookAt[], footnote, footAt, out, w, vocabLabel, entriesNote, noEntry"
variants: "English hits vs Indic misses"
last_used: system-design-of-ai/12-tokenizers
---
# TokenDictionary

**Purpose:** a metaphor for a tokenizer vocabulary: a fixed dictionary whose entries are whole (mostly English) words. Incoming words look up their entry; found = one orange token block, not found = the word breaks into smaller TokenBlocks pieces. Reusable for any "vocabulary / lookup table" explanation.

**Props:** `entries` (words printed as whole dictionary entries, e.g. Friday, order, refund, delivery), `words` (incoming words in order: `{text, found:true}` or `{text, found:false, pieces:[…]}` with real tokenizer pieces), `footnote` (dim-grey line, e.g. "vocabulary built from training text, mostly English"), `w`, `at` (book opens), `lookAt` (frame of each lookup, array or start+stagger), `out`.

**Look**
- An open book drawn flat: two white pages with 2 px border and 14 px radius, a spine line, thin rule lines; entries in Instrument Serif Italic (headword) with a tiny id number in JetBrains Mono.
- Incoming word: Inter 700 pill above the book. Found: the matching entry gets an orange ring and the pill collapses into one orange TokenBlocks block. Not found: a dim "no entry" mark, then the pill cracks into its pieces as white TokenBlocks blocks.
- Output row of blocks sits under the book (same block style as TokenBlocks).

**Motion**
- Book opens with a spring (pages scale X from the spine). Each lookup: pill slides down (spring), searches (entry highlight sweeps), then collapses or splits (pieces spread with 4-frame stagger). Everything exits.

**Sound:** page-flip whoosh on open, `pop` on a found entry, `typing-tick` per piece on a split.

## Code

Saved: `components/code/TokenDictionary/TokenDictionary.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values and the Noto Sans Devanagari/Bengali fonts come from `components/code/theme.ts`.

- First built and rendered in `system-design-of-ai/12-tokenizers`.
