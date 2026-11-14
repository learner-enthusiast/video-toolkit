---
name: carousel
description: Turn a reel's script.md into a 6–8 slide Instagram carousel (1080x1350 PNGs + PDF, caption, alt text) in out/carousel/.
argument-hint: <project>
---

# Carousel (4:5, 1080x1350, 6–8 slides)

The reel's "carousel twin": the same points as the script, as swipeable slides people save. Runs inside Stage 4 · Deliver of every 9:16 reel (`pipeline/stages.md`), or on its own for an older project. Read `CLAUDE.md`, `brand.md`, `pipeline/carousel.md` and `components/Carousel.md` first; `brand.md` wins. Choose any other components from `components/INDEX.md` first.

**Input:** `projects/<project>/script.md` and `assets/logos/` (if present). If `<project>` is missing or has no `script.md`, stop and tell me.
- Never invent a fact, number or claim the script doesn't say. Shorten its wording; don't add to it.
- Use the script's glossary spellings exactly. Captions-style fixes from `log.md` (intended words over misspoken ones) apply here too.
- Never touch `raw/` or `assets/`. A new logo goes in `assets/logos/` only with its source in `SOURCES.md`, and only if I asked for new assets; otherwise copy into `work/`.

**Slide plan (6–8 slides)**
- **1 · Hook:** the reel's opening question or claim, biggest type.
- **2 · Problem:** what breaks without the concept.
- **3 … N-2 · One idea per slide:** the solution, key terms, how it works. It may carry a small diagram, a code block or a logo.
- **N-1 · Recap:** 3 bullets max.
- **N · CTA:** "Save this for your interview" + the follow handle.

Merge script sections to fit the count; a 13-section script still makes ≤ 8 slides. Order follows the script.

**Steps**
1. **Outline.** Write `work/carousel/outline.md`: per slide, its type, the exact on-slide text with a word count (≤ ~25), the highlight word(s), and a visual note. Add the draft `caption.txt` and alt text at the end. **Stop and ask me to approve it.**
2. **Look.** Build the renderer (`components/Carousel.md`) and render slide 1 only to `work/carousel/stills/01.png`. Open it and check it yourself first, then **stop and ask me to approve the look.**
3. **Render.** Render every slide to `out/carousel/01.png … 0N.png` in one bundle (`renderStill` in a loop). Build `carousel.pdf` with `img2pdf` (lossless, page = 1080x1350), and write `caption.txt` and `alt-text.txt`.
4. **QA:** `pipeline/carousel.md` → QA. Open every PNG yourself. Fix and re-render any slide that fails, then re-check it.
5. **Log** the run in `log.md` (`pipeline/project-log.md`) and report the files plus anything not done as specified.

Rendering is a heavy exact-command job (Haiku batch); PDF assembly and file shuffling are low-stakes (delegation order in `pipeline/delegation.md`). The slide code, layout and every visual judgment stay with Opus.
