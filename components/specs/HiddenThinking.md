# HiddenThinking

**Purpose:** reasoning tokens are billed but never shown: the short reply the user sees next to a far taller stack of hidden "thinking" pages, each charged.

**Props:** `at`, `thinkAt` (pages start), `labelAt` ("reasoning tokens · billed"), `neverAt` ("✕ not in the reply"), `linesAt` / `pagesAt` (the punch), `pages` (~18), `out`. Dark style.

**Look**
- Right: reply card (#1A1A1A, white border) with 10 short white lines, labelled "what the user sees". Left: a stack of grey pages (#2A2A2A, white 35% border, faint text lines), 46 px apart, each with a small orange ₹ coin at its corner. Orange pill "reasoning tokens · billed" over the stack.
- Punch in screen space: "10 lines" (white) over "N+ pages" (orange), Inter 900 ~64 px.

**Motion**
- Pages drop in one every 3 frames from `thinkAt`, each ₹ pops as its page lands. On `pagesAt` the scene pulls back (scale 1 → ~0.72 from the top centre) to show the stack runs far past the reply.

**Gotchas**
- A pull-back stronger than ~0.7 shrinks the reply card and labels below phone readability; use fewer pages instead.
- The page count is illustrative; never put a token number on it.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
