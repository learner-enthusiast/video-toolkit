# VectorSpaceMiss

**Purpose:** show why similarity search retrieves the wrong chunk: the query lands near what sounds like it, while the chunk that decides the answer sits far away and is never fetched.

**Props:** `query` (label), `near` cards (title, sub, score), `hit` (the card retrieved), `far` (the ignored card), `phases`: search (`qAt`, `linesAt`, `hitAt`, `textAt`, `phraseAt`), miss (`wrongAt`, `panAt`, `farAt`), gap (`cancelAt`, `noWordsAt`).

**Look**
- A 2D field of small warm-grey dots on the grid card. The query is an orange dot with a soft pulsing halo and a label.
- Chunk cards: white, 2 px border, title + one-line sub. Similarity lines from the query carry a mono score pill (0.91, 0.74…).
- Retrieved card: orange border and title, opens to show its text with the key phrase on the orange block.
- Ignored card: dashed warm-grey border, dim text, tag "never retrieved". When named, it becomes solid.
- Gap view: the two cards far apart; a grey dashed low-score line from the query to the far card; an orange dotted curved arrow from the far card to the retrieved one ("cancels it": linked by meaning, not by words).

**Motion**
- Lines draw from the query outward (10 frames, staggered). The hit lights on its spoken name.
- Miss: on "wrong" a hard cut to dark style (tick and lines dim to grey, WRONG stamp), then the camera pans (ease-in-out, ~44 frames) to the far card.

**Gotchas**
- Scores and extra chunk names are illustrative; keep them plausible and never present them as measured.
- Quote statute or document text exactly, with ellipses where shortened.
- Draw the world once in world coordinates and move a camera; do not re-lay it out per phase (the gap view may use its own compact layout).
