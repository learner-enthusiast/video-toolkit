# Brand 2 (Terminal, dark)

Theme: `components/code/themes/brand2.ts`. Shared rules: `brand.md`. Reference (the idea, not a copy): srvjha reels "Incognito mode doesn't make you anonymous", "Retrying an LLM call", "Power failure / WAL".

**Colors**
- Page `bg #0A0F0D`, card `surface #111814`, `border #1F2A25`, grid `#16201B`. Text `#EAF2EE`, dim `textDim #7E8B85`.
- Green `accent #3DFFA2`: UI, kickers and captions. Amber `accent2 #FFC23D`: the focused card's border and glow, key words and the highlighter. Text on an accent fill: `onAccent #06120C`.
- Alert red `alert #FF4D4D`: only for failure punch stamps ("POWER FAILURE"), never for good/bad states.
- Bad = dim + amber warning mark; good = green.
- Dark fills `#000000`; punch moments: pure black `#000000` with white text.

**Background**
- Near-black with a faint 40 px grid, subtle scanlines and a vignette (`gridBg()` draws all three). Punch: pure black.

**Type**
- Headlines: Inter 800, white, key words in amber.
- Kicker: JetBrains Mono caps, letter-spacing 0.2em, with a leading dash ("— AI SYSTEM DESIGN · EP 05").
- Code and labels: JetBrains Mono.

**Shape**
- 14 px radius, 1–2 px borders, one soft shadow `0 10px 28px rgba(0,0,0,.5)`. The focused card gets a 2 px amber border + a soft amber glow.

**Captions**
- Inter Black caps, white; the current emphasis word on an amber block with dark text. One or two words at a time.
- Burned in, in every state. 9:16 HEAD: lower third on a block of the page colour, never over the face. 9:16 SPLIT: on the strip between the grid card and the docked talking head. 9:16 FULL: a band just below the graphic or above the platform overlay, never over its key element.
- 16:9: bottom center inside the safe margin, at most 2 lines.

**3D**
- Near-black materials, light edges, green highlights, amber on the focused object. Soft even lighting, isometric-style camera with a slow orbit, no default Three.js look.

**Signature components** (`components/code/brand2/`)
- `CamFrame`, `HighlighterText`, `ReceiptCard`, `AlertFlash`.
