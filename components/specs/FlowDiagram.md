---
code: components/code/FlowDiagram/FlowDiagram.tsx
preview: components/code/FlowDiagram/preview.png
props: "FlowLanes: aAt, failAt, bAt, retryAt, n, failIdx, cell, labels {a,b,redo,retry}, at, out"
variants: "lanes (one big call vs N small calls); node/edge builder spec-only"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
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

## Variant: `FlowLanes` (added for system-design-of-ai/11-max-tokens-and-truncation)

Two stacked lanes comparing one big call against N small calls. Lane A: one card holding N cells; on `failAt` every cell from `failIdx` on turns dim dashed with ⚠ and a "redo all" note pops. Lane B: N separate cells that tick orange one by one (5-frame stagger); cell `failIdx` fails, then on `retryAt` it retries orange with a "retry, bigger budget" tag. Sound: `pop` per lane, `soft-pop` on the failure, `pop` on the retry.

## Code

Saved: `components/code/FlowDiagram/FlowDiagram.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: FlowLanes: aAt, failAt, bAt, retryAt, n, failIdx, cell, labels {a,b,redo,retry}, at, out.
- First built and rendered in `system-design-of-ai/11-max-tokens-and-truncation`.
