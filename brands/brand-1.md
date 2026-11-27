# Brand 1 (light, notebook) — the default

Editorial, clean, "notebook" feel. Theme: `components/code/themes/brand1.ts`. Shared rules (layout, motion, icons, end card): `brand.md`.

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
- Burned in, in every state. 9:16 HEAD: lower third on an off-white block, never over the face. 9:16 SPLIT: on the off-white strip between the grid card and the docked talking head. 9:16 FULL: a band just below the graphic or above the platform overlay, never over its key element.
- 16:9: bottom center inside the safe margin, at most 2 lines.

**3D**
- Off-white/cream materials, near-black edges (outlines), orange highlights. Soft even lighting, no harsh shadows, no default Three.js look. Isometric-style camera with a slow orbit.
