---
code: components/code/SourceChip/SourceChip.tsx
preview: components/code/SourceChip/preview.png
props: "at, logo {file,w,h}, children, size"
variants: "with/without logo"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# SourceChip

**Purpose:** a citation chip under an answer ("Electronics Policy §3.2").

**Props:** `text`, `at`, `out`.

**Look**
- Pill: white fill, 2 px orange border, small doc icon, JetBrains Mono ~26 px.

**Motion**
- Pop in with a spring, then a short orange pulse ring.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/SourceChip/SourceChip.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: at, logo {file,w,h}, children, size.
- Logo files come from icons/logos/ (icons/icons.md).
