# Buildings

**Purpose:** the office analogy: your office (the main domain) and a separate building for visitors (the user-content domain).

**Props:** `office` (`{ label, host, at }`), `annex` (`{ label, host, at }`), `visitors` (`at`), `turnAway` (`at`), `moveTo` (`at`), `rect`, `at`, `out`.

**Look**
- Two simple line-drawn buildings (2 px near-black strokes, off-white fill, window grid), the office larger. Labels in Inter Medium (`Office`, `Separate building`) with the host in a JetBrains Mono chip under each (`vercel.com`, `vercel.app`, the varying part orange).
- Visitors: three small near-black dots with a head (generic person glyph, line style).
- Turn-away: an orange curved arrow from the office door back out; a dim "no desks here" is not needed (the arrow says it).

**Motion**
- Buildings draw their outlines (stroke-dashoffset, eased) on their words, windows pop staggered 4 frames.
- Visitors walk (eased) toward the office on `visitors`, the arrow draws on `turnAway`, they walk on to the annex on `moveTo` and the annex windows light orange.
- Exit: fade before `out`.

**Gotchas**
- Generic shapes only; no company logos on the buildings.
