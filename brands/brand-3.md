# Brand 3 (Slate, mild dark)

Theme: `components/code/themes/brand3.ts`. Shared rules: `brand.md`. Reference (the idea, not a copy): srvjha reel "10 AI terms in 60 seconds".

**Colors**
- Page `bg #161B24`, card `surface #1D2431`, `border #2B3445`, grid `#222A37`. Text `#F1F4F9`, dim `textDim #8A93A6`.
- Cyan `#22D3EE` is the only accent. Text on a cyan fill: `onAccent #0B1220`.
- No red or green. Bad = dim + cyan warning mark; good = cyan.
- Dark fills and punch moments: `#0E121A` with white text.

**Background**
- Charcoal-navy with a soft 28 px dot grid (`gridBg()`). Punch: `#0E121A`.

**Cards**
- Surface fill, 2 px border, 14 px radius, one soft shadow `0 10px 28px rgba(0,0,0,.4)`.

**Type**
- Headlines: Inter 800, white, the key word in cyan.
- Kicker: mono caps in a pill.
- Big numbers: JetBrains Mono with a cyan→blue gradient.
- Code and labels: JetBrains Mono.

**Captions**
- White Inter Black in a dark translucent pill; the current word in cyan. One or two words at a time.
- Burned in, in every state. 9:16 HEAD: lower third, never over the face. 9:16 SPLIT: on the strip between the grid card and the docked talking head. 9:16 FULL: a band just below the graphic or above the platform overlay, never over its key element.
- 16:9: bottom center inside the safe margin, at most 2 lines.

**3D**
- Slate materials, light edges, cyan highlights. Soft even lighting, isometric-style camera with a slow orbit, no default Three.js look.

**Signature components** (`components/code/brand3/`)
- `NumberList`, `TimerRing`.
