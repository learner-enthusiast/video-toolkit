# EmbeddingMap

**Purpose:** what an embedding is: each sentence becomes a row of numbers, and the row becomes a point on a 2D "meaning map" where sentences that mean the same thing land close together.

**Props:** `questions` (text, cluster or far), `nums` (4 illustrative numbers per question), `embedAt`, `landAt[]`, `clusterAt`, map box (`x, y, w, h`, which can animate), optional `newDot` and `farDot` for the lookup.

**Look**
- Rows: question bubble (Inter 700, 24 px, no tail) on the left; on the right a mono number row `[ 0.12 -0.80 0.33 0.05 …]` with the first number on a pale orange block. Header pills: "question" and an orange "embedding · a list of numbers".
- Map: white panel, 2 px border, ~46 faint warm-grey background dots (seeded), a "MEANING MAP" pill top left. Dots: orange (the group in focus), ink (other stored), grey (unrelated, dim label), hollow orange ring (a new query).
- Cluster: a dashed orange ring with a short leader label ("same meaning").

**Motion**
- Numbers fade in one by one (2-frame stagger) on "embedding"; each row squeezes right and fades (10 frames) as its dot flies 14 frames into the map and lands with a small overshoot. Stagger rows 6 frames.
- The map can rise (ease-in-out ~18 frames) to make room for a code card below: draw dots in scene coordinates offset by the map's y, never inside the clipped panel, or flying dots get cut off.

**Gotchas**
- Numbers and distances are illustrative; keep them plausible (similar rows for similar questions) and never call them measured.
- The cluster must look tight next to the unrelated dot: ≥ 4× the cluster radius between them.
- Labels on dots collide fast; give each dot one label side and check it in a still.
