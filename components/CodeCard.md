# CodeCard

**Purpose:** a short code listing whose lines light up in the order I talk about them: which line does the work at each step of a flow.

**Props:** `lines` (string[]), `at` (typing start), `cps` (chars per frame, 4–7), `size` (font px, ≥ 28 in a 9:16 card), `width`, `hl` (list of `{line, at, off?, from?, to?}`: whole-line or character-range highlights), `logo` (optional tech logo in the header), pills (default "server" + "pseudo-code").

**Look**
- White panel, 2 px near-black border, brand radius and shadow. Header strip (~46 px, `#FBFAF7`, 2 px grid-colour rule under it): three small dots (first orange) on the left; on the right an optional logo, then the pills: **"server"** (ink, orange dot) and **"pseudo-code"** (white). Pills: JetBrains Mono 700, 20 px, full radius, 2 px border.
- Code: JetBrains Mono 500, near-black; comments warm grey. Line height 1.38.
- Whole-line highlight: an orange block behind the line, text turns white. Range highlight: orange block behind the characters only.

**Motion**
- Lines type in order at `cps`. A highlight fades in over 6 frames on its word and, with `off`, out over 8 frames when the next step starts, so only the line being spoken is lit.
- The card enters with the standard fade-rise; exits with its scene.

**Gotchas**
- Wrap long lines instead of shrinking the font: a 9:16 card (912 px inner) fits ~50 characters at 28 px. Move trailing comments to their own line.
- If the script gives the code its own beat but the lines are spoken during a diagram, put the card under the diagram in the same FULL card and light each line on its word (`pipeline/composition.md`).
- Highlight the long line and badge only short lines; a badge at the right edge covers the end of a long one.
