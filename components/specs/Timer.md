# Timer

**Purpose:** "the two seconds after you click": a stopwatch that runs 0.00 → 2.00 s, with a step counter that snaps to "9 steps".

**Props:** `seconds` (2), `at` (start), `dur` (frames the needle takes; it may run faster than real time), `steps` ({n: 9, at}), `out`, `rect`, `dark` (bool).

**Look**
- A round stopwatch face (~420 px), white with a 2 px near-black border and a crown on top; 60 tick marks in warm grey, every 5th near-black. An orange sweep arc fills as time runs, an orange needle.
- Readout in the centre: JetBrains Mono 700 ~96 px, tabular, `0.00 s` → `2.00 s`.
- Step counter beside/below it: "9" in Inter 900 160 px orange with "steps" in Instrument Serif Italic 64 px.
- In `dark` (HEAD punch over the dimmed wall), the face stays white; the counter text turns white with the orange number.

**Motion**
- `at`: the watch pops in (scale 0.8 → 1, `pop`), the crown presses down 6 px (button click SFX "tick").
- Needle and arc run eased in-out over `dur`; the readout follows the same curve. At 2.00 a single 4% scale bump.
- `steps.at`: the counter rolls from 1 to 9 (eased-out, 10 frames), then lands with a `pop`.
- Exit at `out`: scale 0.9 and fade, 9 frames.

**Gotchas**
- In HEAD the stopwatch sits on the wall above the head (y ≈ 120–560), never on the face.
