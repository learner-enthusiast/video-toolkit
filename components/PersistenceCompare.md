# PersistenceCompare

**Purpose:** compare periodic snapshots with an append-only log and land the cost of each (here: Redis RDB vs AOF).

**Props:** `w`, `h`, `snapAt`, `aofAt`, `logsAt`, `glowAt`, `stampAt`, `out`.

**Look**
- Two white cards (2 px border, radius 14, shadow). Left: camera icon, a timeline with three "full copy" blocks, dim caption "every few minutes".
- Right: a document card with a folded corner and a clipped log viewport of mono 30 px command lines.
- The right card gets an orange border and a soft orange ring on `glowAt`. A stamp lands low in the box.

**Motion**
- Cards pop at their frames; icons and the timeline draw themselves; copy blocks appear every 20 frames.
- One log line is appended every 8 frames from `logsAt`; older lines scroll up on an eased 6-frame step and clip.
- Glow ring is `box-shadow 0 0 0 8px rgba(228,87,46,.18)` eased in over 10 frames.

**Gotchas**
- The viewport holds 7 rows; only the last ~10 lines are rendered, so it stays cheap on long runs.
- Titles wrap to two lines on narrow cards; keep the 80 px title block.
- The stamp text must match the spoken number.
