---
code: components/code/PrefixMatch/PrefixMatch.tsx
preview: components/code/PrefixMatch/preview.png
props: "rows, labels, at, step, size, pulseAt, reusedLabel(n), restLabel"
variants: "partial match · break at token one"
last_used: system-design-of-ai/09-prompt-caching
---
# PrefixMatch

**Purpose:** show how a prompt cache matches: two prompts as token rows compared from the left; matched tokens get an orange ✓, the first different token gets ⚠, and everything after it dims as "full price". Teaches "identical from the very first token, or nothing".

**Props:** `rows` ([string[], string[]], the two prompts as tokens), `labels` (row labels, default "request 1/2"), `at` (frame the scan starts), `step` (frames per token), `size`, `pulseAt` (pulse the first cell on "very first token").

**Look**
- Token cells: mono text, 8 px radius. Matched: orange 3 px border + pale-orange fill, ✓ under the second row. Mismatch: dim border, mute fill, ⚠ under it. After the mismatch: dim text at ~45% opacity.
- Summary pills after the scan: "reused: N tokens" (orange) or "nothing reused" (dim) + "the rest: full price" (dim).

**Motion**
- Rows enter (spring) 5 frames apart; the scan moves one cell every `step` frames; the summary pops when the scan passes the mismatch. Exit via the scene wrapper.

**Sound:** one `tick` per matched cell (−4 dB), `soft-pop` on the ⚠.

**Gotchas**
- Brand: no red/green; ✓ orange, ⚠ dim grey. A mismatch at index 0 is the "cache hit rate 0%" case: use it for the broken-template beat.
- Keep rows ≤ ~8 tokens at size 28 in a 972 px card, or the row runs past the right margin.
