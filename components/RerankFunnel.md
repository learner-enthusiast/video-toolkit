# RerankFunnel

**Purpose:** ~50 candidate cards pass through a cross-encoder box, get scored, reshuffle, and the top 5 exit glowing orange.

**Props:** `n`, `boxAt`, `scoreAt`, `keepAt`, `keep` (5), `rect`, `out`.

**Look**
- Small cards in a grid above; a central box labelled "Cross-encoder" showing [question | chunk] side by side; score numbers (0.00–1.00, mono) flash on cards.
- Top 5 orange with a soft orange glow; the rest dim grey.

**Motion**
- Cards stream into the box (stagger 1 frame), emerge with scores, re-sort by score with springs; the 45 others fade and sink, top 5 rise.

**Gotchas**
- Keep ≤ 50 DOM cards; deterministic scores from a seed.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
