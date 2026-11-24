# Web capture (screenshots and screen clips)

**Goal:** Claude takes every web still a video needs itself, with Playwright, instead of me supplying them: articles, docs, GitHub pages, changelogs, pricing pages, status pages, market data pages, my own sites. Captured on purpose for the frame they'll appear in, so they're sharp, clean and already know where the important part is.

**When:** Stage 1 · Prep, after the voice-cleaning gate and transcription, from the script's `## Web captures` list (or the prompt's). Also in Compose, when a beat turns out to need a still nobody listed. I only supply what's private or behind my own login, in `assets/`.

**Tools**
- Playwright (Chromium) is installed for this toolkit (`/setup` checks it). Use the Playwright MCP tools if they're connected in the session; otherwise write a small script in `work/captures/capture.mjs` (Node, `playwright` installed globally) and run it. Reuse the same script for the whole project: one browser, many pages.
- Fetching a page's text (to find the right paragraph, number or date) is fine with any web tool; the screenshot itself always comes from Playwright.

**Where files go**
- `projects/<name>/work/captures/<NN>-<slug>.png` (and `.webm`/`.mp4` for clips). Never in `assets/` (mine, read-only) or `raw/`.
- `work/captures/captures.md`: one row per file: file, URL, captured at (local time with timezone), viewport and scale, what it shows, the beat it's for, focus boxes, private data blurred (yes/no).
- `work/captures/<NN>-<slug>.boxes.json`: the pixel boxes of the elements that matter (see Focus boxes). Copy the PNGs into `work/remotion/public/` at Compose, as with any media.

**Capture for the frame**
- Decide the target first: which layout state (FULL, SPLIT's top card, `ScreenshotKenBurns`, `ZoomCard`, thumbnail, LinkedIn photo) and the on-screen box size in px.
- Shoot at `deviceScaleFactor: 2` (3 for small elements) so a zoom up to 2x stays sharp, the `ScreenshotKenBurns` limit.
- Viewport by target: desktop pages 1440x900; a 9:16 FULL that shows a page top-to-bottom, a mobile viewport (`devices['iPhone 15 Pro']` or 430x932) so the text is big; the SPLIT top card, 1200x900.
- Prefer element screenshots (`locator.screenshot()`) for one thing (a paragraph, a code block, a chart, a pricing row, a post) over a whole page with the point lost in it. Add ~24 px padding with `clip` or a wrapper so nothing touches the edge.
- Use `fullPage: true` only for a scroll-through beat (a long changelog, a doc page), then pan it with `ScreenshotKenBurns` keys.
- Make text bigger when the page is dense: `page.evaluate(() => document.body.style.zoom = '1.25')` or a `font-size` bump, so it reads on a phone. Never above what still looks like the real page.
- Theme: `colorScheme: 'light'` by default (sits well on the off-white brand); `'dark'` when the beat is in the dark punch style.

**Clean the page before the shot**
- Wait for `networkidle`, then for fonts (`document.fonts.ready`) and lazy images (scroll the target into view first).
- Close or hide cookie banners, newsletter pop-ups, chat widgets, sticky headers/footers and ads: click "Reject"/"Close" when there is one, otherwise hide them with injected CSS (`page.addStyleTag`). Never alter the content itself: no edited text, numbers, dates or headlines.
- Keep the evidence: for news and incidents, the headline, the outlet name and the date stay in the shot.
- Blur personal data (other people's emails, names in comments, tokens, account IDs) on a copy, per `ScreenshotKenBurns` → Gotchas.

**Focus boxes (the "better stills" part)**
- For every region the script will point at, get its box from the DOM (`locator.boundingBox()`, times the scale factor) and save it in the `.boxes.json` with a name: `{"headline": [x, y, w, h], "price-row": [...]}`.
- Those boxes feed `ScreenshotKenBurns` `keys` and `Highlight` `box` directly, so zooms and highlights land exactly on the words instead of being guessed from the image.
- Also capture the page `<title>` and canonical URL for the `UrlPill` (scheme dropped) and the `SourceChip`.

**Screen clips (motion)**
- Use a still + `ScreenshotKenBurns` first; it's sharper and easier to time to my words.
- Record a clip only for something that has to move: a UI interaction, a typing demo, a hover state, an animation on the page. Use `recordVideo` at the viewport size (scale 1), script the clicks with short `waitForTimeout` gaps, keep it ≤ 8 s, then re-encode to the project's fps with ffmpeg on the GPU (`pipeline/gpu.md`).

**Limits**
- Public pages only. No logging in with my accounts unless the prompt says so; anything behind my login, I supply.
- Paywalled articles: only what shows before the paywall (headline, standfirst, date).
- No photos of real people as stills (crop to the text; `QuoteCard` handles quotes). No video frames from other creators' videos.
- Sites that block automated browsers (X often does): don't work around it. Note it in `captures.md`, rebuild the content as a brand card (`QuoteCard`, `IncidentCard`) from its text, or ask me for a screenshot.
- Market charts: re-draw them from the numbers with `LineChart` (sharper, on-brand); a screenshot of the source page is only the evidence beat.

**QA** (open every capture yourself)
- Size and scale match the plan; text readable at the size it will be on screen (downscale to that size and look).
- No banner, pop-up, ad, sticky bar, scrollbar or loading spinner; fonts loaded, images loaded.
- Content unaltered; date and source visible where the beat is evidence; private data blurred.
- Every focus box lands on its element (draw them on a copy in `work/captures/check/` and look).
- `captures.md` has a row for every file.