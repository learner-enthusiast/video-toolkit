# Card

**Purpose:** the base container for every panel: company cards, stack boards, code cards and stat panels.

**Props:** `rect` or `x/y/w`, `at`, `out`, `accent` (bool), `children`.

**Look**
- Panel background, 1 px hairline border (2 px accent when `accent`), radius 16 and the brand shadow, from `theme.ts` only.
- Padding is about 28 px. Content uses Inter; code uses JetBrains Mono.
- Company names are text, not logos. Title in Inter 700, meta line in dim text with `·` separators.

**Motion**
- Enter: a spring on opacity, a translateY of 24 px → 0, and scale 0.96 → 1.
- Children (rows, chips) stagger by 4–6 frames.
- Exit: a fade with a slight lift over 8–10 frames before `out`. Never pop off.

**Gotchas**
- Use one card style for the whole video. Do not invent per-beat variants.
- Stack-board rows slide in on the word that names them, not all at once.
