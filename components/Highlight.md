# Highlight

**Purpose:** point at a region of a screenshot when the cue says "highlight".

**Props:** `box` (in image px, the same space as `ScreenshotKenBurns` keys), `at`, `out`, `dim` (default 0.35).

**Look**
- A 3 px accent-colored rounded outline (radius 12) around the box, plus 6–10 px of padding and a soft accent glow.
- The rest of the screen dims slightly (a black overlay at about 35%) with a cut-out hole over the box.

**Motion**
- The outline draws in (stroke) over about 12 frames while the dim fades in.
- An optional single soft pulse after landing.
- Exit: fade both out.

**Gotchas**
- Transform the box through the same Ken Burns transform as the image, every frame, or it slides off target.
- If the element named in the cue doesn't exist in the image, outline the closest real element and add the missing part as a `Tag` graphic. Tell me in the report.
- Keep the outline clear of the bubble rect.
