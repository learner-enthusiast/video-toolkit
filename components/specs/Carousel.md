# Carousel

**Purpose:** one Remotion `Still` per slide of an Instagram carousel (`/carousel`, `pipeline/carousel.md`). Same brand as the reel, so the set reads as its twin.

**Props:** `slides` (from `work/carousel/slides.json`: `type`, `title`, `body` or `bullets`, `hl` words, `visual`), `index`, `total`, `series` (e.g. "Interview Series #9"), `handle` ("Arnab Samanta").

**Canvas:** 1080x1350 (4:5), PNG. 80 px safe margin on every side → a 920x1190 content box.

**Zones** (y from the top)
- **Header** 80–150: series pill (2 px border, full radius, orange dot) on the left, the topic in dim Inter 600 on the right. Same on every slide.
- **Body** 190–1130: the slide content, top-aligned on one 12-column grid. Nothing below 1130.
- **Footer** 1190–1270: handle in Inter 600 bottom-left. Bottom-right 260x110 box is reserved: the counter `2/7` (Inter 700, tabular) and an orange swipe arrow, on every slide but the last. Nothing else may enter that box.

**Type scale** (body text never below 40 px)
- Hook headline: Instrument Serif Italic, orange, 130–150 px, ≤ 3 lines.
- Slide title: Instrument Serif Italic, orange, 84–96 px, ≤ 2 lines.
- Body and bullets: Inter 500, near-black, 44–52 px, line-height 1.3, ≤ ~25 words a slide.
- Labels inside diagrams: Inter 600, ≥ 40 px. Code: JetBrains Mono ≥ 40 px, ≤ 6 lines, ≤ 28 characters a line.
- Chrome (pill, topic, handle, counter): Inter 600–700, 34–38 px.

**Slide types**
- `hook`: dark style (`#0D0D0D`, white text, orange headline): the scroll-stopper. Kicker line + headline.
- `problem`: title + 1–2 lines, with the broken thing dimmed to warm grey and an orange warning mark.
- `idea`: title + body, plus one optional visual: a small diagram (Card boxes + FlowArrow), a code card, or a logo tile. Step numbers only when the script itself numbers the steps.
- `recap`: title + ≤ 3 bullets, an orange square marker on each.
- `cta`: "Save this for your interview" as the headline, the follow handle on a white block, no counter or arrow.

**Look**
- Off-white page with the ~40 px notebook grid (`#DCD8D0`), cards white with the brand 2 px border, 14 px radius and the one soft shadow (`brand.md`). The hook's dark style has no shadow.
- Emphasis from `brand.md` only: an orange block behind a key word, or orange text. At most 2 highlights a slide.
- Logos only from `assets/logos/` (copied to `public/`), `object-fit: contain`, on a white tile on the dark slide.

**Gotchas**
- No red/green, no emojis; bad = warm grey + orange warning mark, good = orange.
- Text must fit by wording, never by shrinking below the scale: cut words in the outline instead.
- Reuse the project's `theme.ts` and fonts (`work/remotion/src/lib/theme.ts`); load fonts with `@remotion/google-fonts` and wait for them (`delayRender`) or the first still renders in a fallback font.
