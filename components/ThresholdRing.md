# ThresholdRing

**Purpose:** a similarity threshold drawn as a ring around a stored point: anything that lands inside counts as "the same". Strict ring = right hits; a loose ring swallows a point that means the opposite.

**Props:** `x, y` (centre), `r` (start radius), `at` (draw), `steps` (`[{at, r}]` radius changes), `dashed` (a soft grouping ring, not a threshold), `label`, `labelAt`, `width`.

**Look**
- Orange stroke (5 px), orange fill at 8% opacity. Solid when it is the threshold; dashed (14/10) when it only groups a cluster.
- Label: a 34 px leader line from the ring's upper-right (45°) and Inter 800 24 px orange text ("threshold 0.1", "too loose").

**Motion**
- Draws itself clockwise from 12 o'clock over 14 frames (ease-in-out).
- Radius changes spring (damping 13, stiffness 90, small overshoot) on the word: grows on "too loose", shrinks back on "strict".
- Pair with a Stamp (HIT orange inside, ⚠ "Same answer served" when the wrong point is swallowed).

**Gotchas**
- Size the loose ring so it clearly contains both points with margin; a point on the edge reads as ambiguous.
- Keep the label outside the map's other dot labels; check the grown radius in a still, since the leader moves with it.
- A small version (two dots, ring 70 → 36 px) works as a checklist icon for "keep the threshold strict".
