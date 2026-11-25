# LinkedInPhoto

**Purpose:** the single image on a LinkedIn text post (`/text-posts`, `pipeline/text-posts.md`). Its only job is to stop the scroll so people read the post. Content, never my talking head. Also renders the X Article header (wide variant).

**Props:** `headline` (≤ 8 words), `hl` (≤ 2 highlight words), `kicker` (optional, ≤ 6 words, e.g. "Redis · cache invalidation"), `visual` (one of: `stat`, `beforeAfter`, `diagram`, `code`, `chart`, `logoPair`), `visualProps`, `style` (`light` | `dark`), `handle` ("Arnab Samanta"), `variant` (`linkedin` | `xHeader`). All from `work/text-posts/photo.json`.

**Canvas**
- `linkedin`: 1080x1350 (4:5, takes the most room in the mobile feed), PNG. 80 px safe margin → a 920x1190 content box.
- `xHeader`: 1500x600 (5:2), PNG. 60 px margin. Headline left, visual right; the same look so the two read as one brand.

**Zones** (`linkedin`, y from the top)
- **Kicker** 80–140: optional series/topic pill (2 px border, full radius, orange dot).
- **Headline** 170–~560: Instrument Serif Italic, 110–140 px, ≤ 3 lines, orange; highlight word(s) on the orange block with near-black or white text.
- **Visual** ~600–1170: one visual, big. Labels Inter 600 ≥ 40 px; numbers Inter Black 140–220 px; code JetBrains Mono ≥ 40 px, ≤ 6 lines.
- **Footer** 1190–1270: handle in Inter 600, 34–38 px, bottom-left. Nothing else.

**Visual types**
- `stat`: one huge number from the script + a 3–6 word label ("₹4.2 lakh wasted / month"). Strongest default when the script has a number.
- `beforeAfter`: two cards side by side or stacked; the bad one dimmed to warm grey with an orange warning mark, the good one in orange (no red/green).
- `diagram`: ≤ 4 boxes (Card + FlowArrow), one orange path showing the point.
- `code`: a code card with the one line that matters highlighted on the orange block.
- `chart`: one line or bar chart, the key point marked with an orange dot and a label.
- `logoPair`: two official logos on white tiles with a vs / → between them, for tool comparisons.

**Look**
- `light`: off-white page with the ~40 px notebook grid (`#DCD8D0`), cards white with the 2 px border, 14 px radius and the one soft shadow (`brand.md`).
- `dark`: `#0D0D0D`, white text, orange headline, no shadow. Use it when the hook is a warning or a shock number; it stands out more in LinkedIn's white feed.
- At most 2 highlights. One visual only: if two ideas compete, cut one.

**Gotchas**
- No face, no talking-head frame, no screenshot of the video.
- No red/green, no emojis, no tiny text: everything must read at 25% size (270x338). Fit by cutting words, never by shrinking below the scale.
- Never more than 8 words in the headline; the post carries the detail.
- Reuse the project's `theme.ts` and fonts (`work/remotion/src/lib/theme.ts`); wait for fonts (`delayRender`) or the still renders in a fallback font.
- Logos only from `icons/logos/` (copied to `public/`), `object-fit: contain`, on a white tile on the dark style.