# UrlPill

**Purpose:** show the address of the site on screen (e.g. `newsly.arnabsamanta.in`).

**Props:** `url`, `at`, `out`, `cx`, `y`.

**Look**
- A pill at top center inside the safe margin: panel background, hairline border, brand shadow.
- A small lock icon (line style), then the URL in JetBrains Mono 500 at about 28 px. Dim the scheme; never show `https://`.

**Motion**
- Drop in: from y −20 px with a fade (spring), shortly after the screen appears.
- Optionally type the URL in, character by character, over 12–18 frames.
- Exit: fade up.

**Gotchas**
- Keep it clear of the zoomed area of interest; move it if the highlight is at the top.
- In 9:16, place it at the top of the screen half, not at the very top of the frame.
