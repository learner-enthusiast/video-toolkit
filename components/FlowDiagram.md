# FlowDiagram

**Purpose:** architecture or request-path diagrams that build node by node as I say each step.

**Props:** `nodes` (id, label, x, y, w, `at`), `edges` (from, to, `at`, label, tone), `dots` (path, from/to frames), `out`.

**Look**
- Nodes are rounded boxes (radius 16) with JetBrains Mono labels. An active node gets an accent border and a faint glow.
- Edges are 2 px lines with arrowheads, as orthogonal or gently curved paths between box edges (not centers).
- Branches (miss, invalid, error) use dim or red edges, with small labels on the edge.

**Motion**
- Each node fades and scales in at its word. Its incoming edge draws in first (stroke-dashoffset, eased over about 10 frames).
- A travelling dot (accent, with a soft glow) moves along the path in sync with the words, eased between nodes.
- A failure branch flashes red once, then loops back to its retry target.
- Everything exits together with a fade at `out`.

**Gotchas**
- Lay out on the grid inside the free rect, and keep labels short (≤ 18 chars) so the boxes stay even.
- Compute edge points from node rects so moving a node never breaks the arrows.
