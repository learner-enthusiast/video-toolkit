# IconRail

**Purpose:** a row or column of tech icons that appear as each technology is named.

**Props:** `icons` (name, `at`, optional label), `direction`, `size`, `out`.

**Look**
- `simple-icons` SVG paths in white (or brand color when it is readable on dark), inside a 64–80 px square tile with the brand radius, panel background and hairline border.
- An optional small label under each tile in dim Inter 500.
- Tiles are evenly spaced on the free side of the frame.

**Motion**
- Each tile fades and springs up 16 px on its word. Groups stagger 4–6 frames when words are close together.
- Exit together with a fade.

**Gotchas**
- Recent `simple-icons` releases dropped some brands (OpenAI, AWS S3). Install v13 under an npm alias for those. If a brand never existed in the set, use a `Tag` with the name.
- Brand colors that are near-black (e.g. Next.js) must render white on the dark background.
- Never use emoji or hand-drawn logos.
