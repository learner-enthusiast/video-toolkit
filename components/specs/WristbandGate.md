# WristbandGate

**Purpose:** the JWT analogy: a concert gate where the guard checks a wristband, not a guest list.

**Props:** `gateAt`, `wristbandAt`, `noListAt` (clipboard crossed out), `checkAt` (guard glance + tick), `passAt` (person walks through), `rect`, `out`.

**Look**
- Flat line illustration in near-black strokes on the grid card: a gate arch, a guard figure, a person with an orange wristband on a raised wrist.
- Clipboard icon in warm grey with a thin orange strike-through on `noListAt`.
- A small orange tick badge on the wristband on `checkAt`.

**Motion**
- Gate and guard draw in (stroke) on `gateAt`; the person slides in from the left with a spring.
- Wristband glows orange (scale pulse 1 → 1.1 → 1) on `wristbandAt`.
- Person walks through the gate (translateX ease-in-out) on `passAt`.
- Exit: fade 8 frames.

**Gotchas**
- No emojis, no stock-clipart: simple line icons only.
