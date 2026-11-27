# Carousel

**Purpose:** one Remotion `Still` per slide of an Instagram carousel (`/carousel`, `pipeline/carousel.md`). Same brand as the reel, so the set reads as its twin.

**Props:** `slides` (from `work/carousel/slides.json`: `type`, `title`, `body` or `bullets`, `hl` words, `visual`), `index`, `total`, `series` (e.g. "Interview Series #9"), `handle` ("Arnab Samanta").

**Canvas:** 1080x1350 (4:5), PNG. 80 px safe margin on every side → a 920x1190 content box.

**Zones** (y from the top)
- **Header** 80–150: series pill (2 px border, full radius, accent dot) on the left, the topic in dim Inter 600 on the right. Same on every slide.
- **Body** 190–1130: the slide content, top-aligned on one 12-column grid. Nothing below 1130.
- **Footer** 1190–1270: handle in Inter 600 bottom-left. Bottom-right 260x110 box is reserved: the counter `2/7` (Inter 700, tabular) and an accent swipe arrow, on every slide but the last. Nothing else may enter that box.

**Type scale** (body text never below 40 px)
- Hook headline: the brand's headline font, accent colour, 130–150 px, ≤ 3 lines.
- Slide title: the brand's headline font, accent colour, 84–96 px, ≤ 2 lines.
- Body and bullets: Inter 500, the brand's text colour, 44–52 px, line-height 1.3, ≤ ~25 words a slide.
- Labels inside diagrams: Inter 600, ≥ 40 px. Code: JetBrains Mono ≥ 40 px, ≤ 6 lines, ≤ 28 characters a line.
- Chrome (pill, topic, handle, counter): Inter 600–700, 34–38 px.

**Slide types**
- `hook`: the brand's punch style (punch background, white text, accent headline): the scroll-stopper. Kicker line + headline.
- `problem`: title + 1–2 lines, with the broken thing dimmed and a warning mark in the brand's focus accent.
- `idea`: title + body, plus one optional visual: a small diagram (Card boxes + FlowArrow), a code card, or a logo tile. Step numbers only when the script itself numbers the steps.
- `recap`: title + ≤ 3 bullets, an accent square marker on each.
- `cta`: "Save this for your interview" as the headline, the follow handle on a white block, no counter or arrow.

**Look**
- The video's brand background and grid pattern (`brands/brand-N.md`), cards on the brand's card fill with the 2 px border, 14 px radius and the one soft shadow. The hook's punch style has no shadow.
- Emphasis from the brand file only: an accent block behind a key word, or accent text. At most 2 highlights a slide.
- Logos only from `icons/` (`staticFile('icons/logos/<file>')`; `CLAUDE.md`, Icons), `object-fit: contain`, on a white tile on the dark slide.

**Gotchas**
- No red/green good/bad pairs unless the brand file allows them, no emojis; bad = dimmed + warning mark, good = accent.
- Text must fit by wording, never by shrinking below the scale: cut words in the outline instead.
- Reuse the project's `theme.ts` and fonts (`work/remotion/src/lib/theme.ts`); load fonts with `@remotion/google-fonts` and wait for them (`delayRender`) or the first still renders in a fallback font.
