# Thumbnail

**Purpose:** a detailed, concept-first cover: the headline, a picture of the video's actual idea, and me with the mic. The steps are in `pipeline/thumbnail.md`; colours come from the video's brand (`brand.md`).

**Props:** `cutout` (my PNG with alpha), `badge` (series + "EP NN", or a topic kicker), `headline` (lines; ≤ 7 words total), `hl` (the key phrase), `scene` (React node), `texture` (`'none' | 'globe' | 'circuit' | 'document' | 'map' | 'planes'`), `sparks` (default true), `size` (1080x1920 for a reel, the only size it gets; 1280x720 is long-form only).

**Anatomy (1080x1920).** Instagram's profile grid shows a 3:4 centre crop (1080x1440, y 240–1680): everything that matters stays inside it.
- **Badge** (y ≈ 260–330): a pill with the brand radius, a 2 px border, an accent dot and caps at ~30 px; "EP NN" sits on an accent chip.
- **Headline** (y ≈ 340–760): Inter 900, 104–124 px, line-height 0.98, ≤ 3 lines, ≤ ~14 characters per line, in the brand's text colour.
  - `hl` sits on a block in the brand's `accent2`, skewed about −5°, brand radius, padding 0 24 px, in italic Inter 900 in `onAccent`.
  - `sparks`: three short strokes (6 px, round caps) in `accent2` at the end of a headline line.
- **Scene** (y ≈ 720–1300; it may run behind the cutout to y ≈ 1500): 4–8 elements. One focal element has the brand's glow and ring; the rest are neutral or dim.
  - Small mono labels ("Retriever", "Top-K", "Geo Sharding") add detail even when they're unreadable at phone size.
  - Elements wrap around my head (left and right, y ≈ 900–1300), never across my face.
- **Me:** centred, chest-up, with the mic (held, or on its boom arm); head top at y ≈ 1000–1100, chest at the bottom edge of the 3:4 crop.
  - A 2–3 px rim light in the accent.
  - A big, soft accent radial glow behind my shoulders.
- **Background:** never flat. The brand's background (`gridBg()`), the texture at low contrast and a vignette.

**Concept patterns.** Pick exactly one per video, never the same as either of my last two covers.

| Pattern | What it shows |
|---|---|
| `pipeline` | sources → stages → result, with the broken stage marked |
| `beforeAfter` | two windows or cards, the bad one dimmed with a warning tag |
| `evidence` | a real captured page, doc or tweet, tilted, the key line highlighted, a tag |
| `map` | a globe or map with pins, plus a phone |
| `layers` | stacked planes or cards with an accent path through them |
| `device` | a phone, laptop or browser mockup with an invented UI mid-action |
| `numbers` | a shock number, or a numbered row of icons (lists, roadmaps) |

**Per brand**
- Brand 1: light background with a warm accent glow; the headline block in orange.
- Brand 2: black with a neon green and amber glow; the `CamFrame` corners are allowed as a texture.
- Brand 3: slate with a cyan glow.

**Rules**
- **One idea, many details:** headline, scene and face say one thing in a second; the details reward a second look.
- **Real things beat drawings:** real logos, real captured pages, the real code line or number from the video.
- Never fake a real company's UI or quote.
- Cut me out with rembg `birefnet-general` (`birefnet-portrait` drops the mic).
- Add parts the cutout lost with a mic-mask union (`tools/thumbnail/mic_union.py`).
- The whole mic and boom arm are recognisable at 180x320; the arm may run off the canvas edge.
- Place the cutout from its alpha bounding box (hair-top y × scale), not from another video's numbers: how far I sit from the phone changes it.
- Give the face a clear expression and good light; lift exposure on the cutout if needed.
- No text in the bottom-right corner (the duration badge).
- No emojis.

**Gotchas**
- A boom-arm mic fills one side of my head: put that side's elements above it, and wrap the rest round the free side.
- The boom cable can rise into the headline band: the headline draws above the cutout; check no letter is lost against it.
- Brand colours are for the furniture. Official logos keep their own colours (`brand.md`, Icons).

## Code

Template: `templates/remotion/Thumbnail.tsx`, which `tools/scaffold_remotion.py` copies to each new project's `src/lib/`, next to `cues.ts`. It exports `Thumbnail`, `Badge`, `Headline`, `Cutout`, `Background` and the `focal` style, and imports only from `../shared/theme` and shared components.

- `scene` draws behind me; the optional `front` slot draws over me, for elements the boom cable would otherwise cross. Neither goes over my face.
- `focal` is spread after the element's own card style, so its ring wins.
- `cutout` is `{src, w, h, hairTop, faceX}`, measured on the PNG; `place` (`headY`, `scale`, `bleed`) overrides where it lands. `bleed: 'right'` keeps a boom arm running off the canvas edge.
- Not in the library yet: per the library rule (`components/code/README.md`), it moves into its own `Thumbnail` folder in `components/code/` only after it has rendered correctly in a finished video.
