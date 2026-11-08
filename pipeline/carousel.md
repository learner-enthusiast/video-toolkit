# Carousel

**Goal:** a 6–8 slide Instagram carousel twin of every 9:16 reel, in `out/carousel/`. The steps are in `/carousel` (`.claude/skills/carousel/SKILL.md`), the slide layout in `components/Carousel.md`.

**When:** Stage 4 · Deliver, after the final render and its QA, before the report. Also on its own for older projects (`/carousel <project>`).

**Build**
- Source is `script.md` only (plus `assets/logos/`), never the transcript: the slides show the intended words.
- Reuse the project's Remotion setup in `work/remotion/` (theme, fonts, logos in `public/`): add `src/carousel/`, register one `Still` per slide (ids `Carousel-01` …), and a bundle-once render script. If the project has no `work/remotion/` (older projects), create a fresh blank one there per `pipeline/composition.md` → Setup.
- Slide text lives in `work/carousel/slides.json`, written from the approved outline, never typed into the components.
- Render on the GPU (`gpu-run`, `--gl=angle`). If the GPU is busy with a heavy job, render stills on the CPU (`--gl=swangle`) per `CLAUDE.md` and say so.
- PDF: `img2pdf out/carousel/0*.png -o out/carousel/carousel.pdf` (lossless; installed by `/setup`).

**Output** (`out/carousel/`)
```
01.png … 0N.png   slides, 1080x1350, in posting order
carousel.pdf      every slide, one page each (LinkedIn document posts)
caption.txt       hook line, 3-line summary, "Save this", 5–8 hashtags
alt-text.txt      one line per slide: "01: <what the slide shows and says>"
```

**QA** (Opus opens every PNG; a contact sheet alone doesn't pass a slide)
- Size: every PNG is 1080x1350 (`ffprobe` or `identify`), 6–8 of them, numbered without gaps; the PDF has the same page count.
- Text: nothing clipped or overflowing its card, nothing outside the 80 px margin, body ≥ 40 px, ≤ ~25 words a slide.
- Chrome: header and footer identical on every slide; counter right (`3/7`) and arrow present on all but the last; the bottom-right box otherwise empty.
- Brand: colours, fonts, radius, border and shadow from `brand.md`; no red/green, no emojis; logos official and uncropped.
- Words: every term matches the script's glossary spelling; every fact is in `script.md`. Diff the slide text in `slides.json` against the script.
- Contrast: text on the orange block and on the dark slide reads at 25% size (downscale to 270x338 and look).
- Caption: hook line ≤ 125 chars, 5–8 hashtags, total ≤ 2,200 chars. Alt text: one line per slide, same count as the PNGs.
- Fix and re-render failing slides, then re-check them. Never report a pass that wasn't looked at.
