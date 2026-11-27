# Brand

Three brands; each video uses one for every output. Read this file plus **only the active brand's file**. These rules apply to every video (16:9 and 9:16) unless a project says otherwise.

**Brands**

| No. | Name | Look | File | When to use |
|---|---|---|---|---|
| 1 | Notebook | light, off-white, orange | `brands/brand-1.md` | the default |
| 2 | Terminal | dark; green UI, amber focus | `brands/brand-2.md` | when the prompt or script picks 2 |
| 3 | Slate | mild dark, cyan only | `brands/brand-3.md` | when the prompt or script picks 3 |

- **Brand 1 is the default.**
- **Picking it:** a `**Brand:** 1 | 2 | 3` line in the editing prompt and in the project's `script.md`; `work/remotion/.env` holds `REMOTION_BRAND=<n>` (change it only there). Main video, trailer, thumbnail, carousel and LinkedIn photo all use it; a Hindi twin reuses the English graphics, so it matches.
- In older specs, "orange" means the brand's accent and "off-white/white card" means the brand's background/card fill.

**Components**
- One shared component per idea in `components/code/<Name>/`; every colour, font, border, radius and shadow comes from the active theme. Never two copies.
- Props are for content only (text, numbers, frames, rects, logos), never a brand look (existing `dark` props keep working).
- `components/code/brand2/` and `brand3/` hold only signature pieces; if one is needed elsewhere, move it to shared, never copy.

**Shared shape**
- One radius everywhere: 14 px. Safe margin 5% on all sides; the grid is 12 columns inside it.

**Layout: HEAD / FULL / SPLIT**
There is no fixed default layout. Every moment of a video is in exactly one of three states, chosen per beat from what the beat needs. Mix all three through the video. Full spec: `components/specs/layout-states.md`.
- **HEAD:** my face fills the frame, with captions and lower-thirds on top. Story beats, emotion, reactions, transitions, punchlines.
- **FULL:** the graphic fills the whole frame and my face is hidden, while my voice keeps going. Whenever a concept needs the whole screen: flows, code, timelines, comparisons, data.
- **SPLIT:** my face and a graphic together (graphic on top, face docked below: `components/specs/ReelSplit.md`). When my reaction or delivery matters while a simple graphic is on screen: a single card, a short list, a number, a punchline that points at a visual. Never for dense code or detailed diagrams; those go FULL.
- **Switching:** a hard cut or a fluid brand-style wipe (spring or ease-in-out, never linear), only on the beat where a concept starts or ends. Never mid-sentence unless the cut lands on an emphasised word.
- **Script cues** are written `[B07 | mm:ss–mm:ss | HEAD]`, `[… | FULL]`, `[… | SPLIT]`. They are the layout plan; I may move a beat to another state if it explains better (`CLAUDE.md`, Creative direction).
- **9:16 (1080x1920) framing:** HEAD uses a portrait source natively, or a landscape source face-tracked and centre-cropped to portrait. In SPLIT the docked head is a 16:9 window (landscape source) or a head-and-shoulders square on a blurred, darkened copy (portrait source). Keep the face out of the top ~12% and the bottom ~20% platform UI zones, and the docked head lifted clear of the platform caption overlay.
- **Captions** stay on in every state and never sit over a graphic's key element (placement per state in the active brand file's Captions section).

**Motion**
- Fluid and springy, never linear. Lines draw themselves, boxes pop in with a spring, orange packets travel along paths.
- Nothing appears all at once. Reveal in the order I speak about it.
- Animate only with `useCurrentFrame()` / `spring()` / `interpolate()`. Never CSS animations or R3F `useFrame()`.

**Icons and names**
- **Always use the official logo** whenever I mention a company, product or technology that has one (PostgreSQL, Redis, GraphQL, Facebook, Instagram, Threads, Apple for "iPhone"…), shown when it's said. Never a text-written stand-in (a styled word, a coloured pill with the name) in place of a real logo.
- Logos are the one exception to the brand palette: keep their official colours, gradients and shapes. Never recolour, redraw, stretch or crop them (`object-fit: contain`).
- Use the official file (brand/press page, SVG preferred, Wikimedia Commons copy of the official mark, or one I supply), saved in the shared `icons/logos/` library with its source and license in `icons/icons.md` (look it up first with `grep -i '<brand>' icons/icons.md` (never Read it whole); reuse before downloading). Never saved inside a project folder.
- On off-white scenes the logo sits directly on the card. On dark scenes, or where its colours vanish against the background, put it on a small white tile: 2 px `#1A1A1A` border, the brand radius, ~20 px padding. A logo in focus gets an orange ring, and the others dim.
- Only concepts with no official logo (REST, "Orders API", CDN) use a text label or a generic line icon. No emojis.

**End card links**
- arnabsamanta.in
- linkedin.com/in/arnabsmnta
- github.com/learner-enthusiast
- arnabsmnta@gmail.com
