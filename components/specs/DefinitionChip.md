---
code: components/code/DefinitionChip/DefinitionChip.tsx
preview: components/code/DefinitionChip/preview.png
props: "term, def, at, out, size"
variants: "light only"
last_used: system-design-of-ai/06-cancellation
---
# DefinitionChip

**Purpose:** a small inline chip that defines a term the first time it's used ("token = a piece of text you pay for"), so non-experts keep up without a detour.

**Props:** `term`, `def`, `at`, `out`, `size` (default 30), `tone` (light | dark).

**Look**
- Pill (full radius, 2 px border, white fill): the term in JetBrains Mono 700 on an orange block, "=" in dim, the definition in Inter 600 near-black.

**Motion**
- Pops in on the term's word (scale 0.8 → 1), the definition types in quickly (~3 chars/frame); exits with a fade.

**Sound:** `soft-pop`.

**Gotchas**
- One chip per term, first use only. Keep the definition ≤ 32 chars. Never cover the element it explains.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/DefinitionChip/DefinitionChip.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`; glyphs (server, user, handset, chip, warning) from `glyphs.tsx`.

- Code props: term, def, at, out, size.
- First built and rendered in `system-design-of-ai/06-cancellation`.
