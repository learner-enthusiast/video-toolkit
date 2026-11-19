# FeedbackLoop

**Purpose:** a vicious cycle drawn as a circle of nodes that builds node by node, then spins faster and heats up, and can break at one node.

**Props:** `nodes` (labels, each with `at`), `spinFrom`, `heatTo` (red), `breakAt` {node, at}, `rect`, `out`.

**Look**
- 4–6 nodes as pills on a circle, with curved arrows between them (orange). At full heat the arrows and node borders are red.

**Motion**
- Each node pops in at its word, its incoming arrow drawing first.
- From `spinFrom` an orange packet circles the loop, each lap faster (eased acceleration), the colour lerping orange → red.
- Break: the arrow at `breakAt` snaps (a gap opens with a spring), the packet stops there, the colour returns to orange.

**Gotchas**
- Node labels ≤ 22 chars, 2 lines max, so the circle fits a 972 px card at ≥ 30 px.
