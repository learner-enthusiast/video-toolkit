# DiagramBlock

**Purpose:** a labelled box in a flow (Embed → Search → Answer, Docs, Prompt, LLM).

**Props:** `label`, `icon` (generic line icon or logo), `rect`, `tone` (neutral | accent | dim), `at`, `out`.

**Look**
- Card: white fill, 2 px #1A1A1A border, 14 px radius, brand shadow. Label Inter 600 ~40 px, icon above it ~72 px, line style 4 px strokes.
- Accent: orange border + orange icon. Dim: warm grey text, border at 40%.

**Motion**
- Pop in with a spring (scale 0.85 → 1, slight overshoot, fade), groups staggered 4–6 frames.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
