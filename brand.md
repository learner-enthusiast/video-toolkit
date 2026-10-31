# Brand

Editorial, clean, "notebook" feel. Applies to every video (16:9 and 9:16) unless a project says otherwise.

**Colors**
- Page background: warm off-white `#F7F4EE`.
- Grid card: off-white `#F7F4EE` (or white `#FFFFFF` inside it), thin grid lines `#DCD8D0`, 2 px near-black border `#1A1A1A`.
- Accent: orange `#E4572E` for headlines, highlights, arrows and moving packets. It is the only accent.
- Text: near-black `#111111`. Dim text and disabled states: warm grey `#8A857C`.
- Dark style: background `#0D0D0D`, white `#FFFFFF` text, orange accent. Only for punch moments, for contrast.
- No green/red good/bad colors. "Bad" is shown by dimming to warm grey plus an orange warning mark; "good" by orange.

**Fonts** (load via `@remotion/google-fonts`)
- Headlines: Instrument Serif Italic, orange, large.
- Body and labels: Inter Regular/Medium, near-black, revealed word by word.
- Captions: Inter Black (900).
- Code only: JetBrains Mono 400–700.

**Shape**
- One radius everywhere: 14 px (cards, pills use full radius, video frames 14 px).
- Border: 2 px `#1A1A1A` on cards and the docked video. Pills and tags 2 px too.
- Shadow: one soft, flat shadow `0 8px 24px rgba(17,17,17,.08)`. None in dark style.
- Grid card background: a square notebook grid, ~40 px cells, 1 px `#DCD8D0` lines.
- Safe margin 5% on all sides. Grid is 12 columns inside it.

**Emphasis**
- Orange block behind a key word (white or black text on it).
- Orange text on off-white.
- Black text on a white block.

**Captions**
- One or two words at a time, Inter Black, near-black on the off-white background. White in dark style.
- The current word may sit on the orange block for emphasis words only, not every word.
- 9:16 SPLIT: on the off-white strip between the grid card and the docked talking head. 9:16 FULL: lower third, on an off-white block, never over the face.
- 16:9: bottom center inside the safe margin, at most 2 lines.

**Layout (9:16, 1080x1920)**
- FULL: the landscape talking head centre-cropped (face-tracked) to portrait, when no graphic is on screen.
- SPLIT: grid card on top (as tall as the space allows, see below), caption strip in the middle, the full landscape talking head scaled to 1080 wide (~608 px) docked at the bottom with the brand radius and border.
- Portrait source (phone, 1080x1920): FULL uses it natively. In SPLIT, a 16:9 crop of a portrait frame cuts the forehead; show a head-and-shoulders square in the middle of the strip with a blurred, darkened copy filling the sides.
- Keep the docked talking head clear of the platform caption overlay (bottom ~120 px): lift it. With the lift and a caption strip, the grid card is ~970 px tall (not more).
- FULL ↔ SPLIT is a smooth scale + slide (~0.4 s spring). Never a hard cut.

**Motion**
- Fluid and springy, never linear. Lines draw themselves, boxes pop in with a spring, orange packets travel along paths.
- Nothing appears all at once. Reveal in the order I speak about it.
- Animate only with `useCurrentFrame()` / `spring()` / `interpolate()`. Never CSS animations or R3F `useFrame()`.

**3D**
- Off-white/cream materials, near-black edges (outlines), orange highlights. Soft even lighting, no harsh shadows, no default Three.js look. Isometric-style camera with a slow orbit.

**Icons and names**
- **Always use the official logo** whenever I mention a company, product or technology that has one (PostgreSQL, Redis, GraphQL, Facebook, Instagram, Threads, Apple for "iPhone"…), shown when it's said. Never a text-written stand-in (a styled word, a coloured pill with the name) in place of a real logo.
- Logos are the one exception to the brand palette: keep their official colours, gradients and shapes. Never recolour, redraw, stretch or crop them (`object-fit: contain`).
- Use the official file (brand/press page, SVG preferred, Wikimedia Commons copy of the official mark, or one I supply), saved in the project's `assets/logos/` with its source in `assets/logos/SOURCES.md`.
- On off-white scenes the logo sits directly on the card. On dark scenes, or where its colours vanish against the background, put it on a small white tile: 2 px `#1A1A1A` border, the brand radius, ~20 px padding. A logo in focus gets an orange ring, and the others dim.
- Only concepts with no official logo (REST, "Orders API", CDN) use a text label or a generic line icon. No emojis.

**End card links**
- arnabsamanta.in
- linkedin.com/in/arnabsmnta
- github.com/learner-enthusiast
- arnabsmnta@gmail.com
