# PinnedQuestion

**Purpose:** an open question that stays visible in a corner across several scenes, then pops open into a heading when the video answers it.

**Props:** `logo` (e.g. `docker-mark.svg`), `pinAt`, `openAt`, `heading`, `out`, `corner` (frame px of the pinned chip).

**Look**
- Pinned: a 2 px bordered white pill (~96 px tall) with the official logo and an orange "?" in Instrument Serif Italic.
- Open: the pill grows into a wide heading card ("So why is it not a VM?") in Instrument Serif Italic orange, then shrinks/fades away.

**Motion**
- Pin: pops in at a large size where it is introduced, then flies (spring ~0.5 s, ease-in-out path) to its corner and shrinks.
- Idle: a slow ±3° "?" wobble (sine of the frame, ~2 s period) so it never sits dead still.
- Open: spring scale + width morph on `openAt`; exit fade 8 frames.

**Gotchas**
- The corner must stay clear of the platform UI (top 10%, right edge) and of every scene's card content: use the top-left of the SPLIT card or above my head in FULL.
- It is drawn above the layout (not inside the grid card) so FULL ↔ SPLIT morphs don't hide it; move it with the layout.
