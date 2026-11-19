# FridgeMilk

**Purpose:** a kitchen analogy for expiry: check the date when you open the fridge, and sweep the shelves now and then (here: Redis lazy and active expiry).

**Props:** `w`, `h`, `fridgeAt`, `milkAt`, `openAt`, `removeAt`, `onReadAt`, `checkAt`, `sweepAt`, `out`.

**Look**
- A fridge line drawing with a glass door and three shelves; a milk carton and a jar, each with a mono date tag in orange.
- A person with a clipboard (orange tick) beside the fridge. "On read" (orange) and "Random check" (neutral) tags on the right.

**Motion**
- Fridge, shelves and door draw themselves; the carton and jar follow.
- The door swings open by `scaleX` 1 → 0.15 from its hinge (spring). The carton and its date slide out and fade.
- An orange bar sweeps the shelves top to bottom in 16 frames; the jar fades as it passes.

**Gotchas**
- The door is outline-only so the shelves stay visible while it is closed.
- Date tags are HTML overlays; keep their left edge inside the fridge (≤ 380 px).
- Remove the carton before the sweep so the two beats stay readable.
