# ChoicePills

**Purpose:** an either/or question as two pills ("SQL | NoSQL") with a blinking cursor between them, and an optional "wrong answer" glitch.

**Props:** `options` (label, `at`), `cursorAt`, `pick` (index), `glitchAt`, `stamp` (text, `at`, see `Stamp`), `dark` (bool), `rect`, `out`.

**Look**
- Large pills (full radius, 2 px border), label in Inter Black. Light style: white fill, near-black text. Dark style: transparent fill, white border and text.
- A tall orange block cursor between them.
- The picked pill gets an orange fill.

**Motion**
- Pills pop in on their words with a spring, staggered.
- The cursor blinks with a hard on/off every ~15 frames (blinking is the one place a step function is allowed).
- `glitchAt`: the picked pill glitches for ~12 frames: RGB-split offset copies, horizontal slice shifts and a jitter, all seeded with `random(seed)`. Then it dims.
- The `Stamp` lands on top of the glitched pill.
- Exit: fade, or a cut to black when the beat ends on a punch.

**Gotchas**
- Glitch randomness must be seeded and deterministic per frame.
- Never put the pills over my face in FULL layout; use the grid card or dark style.
