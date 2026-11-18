# QuoteCard

**Purpose:** a real public quote from a real person, shown as text only: the quote, name, role and source. Never a screenshot, photo or likeness.

**Props:** `quote`, `name`, `role`, `source` ("X · Jan 6, 2025", "Bg2 Pod · Mar 2026"), `logo` (the company's official mark), `at`, `revealFrom`, `revealTo`, `w`, `size`.

**Look**
- White panel, brand border/radius/shadow, ~44 px padding. A big orange Instrument Serif opening mark (~190 px) hanging off the top-left. Quote in Inter 700 (~46–50 px), near-black. Dashed grid-colour rule, then the logo, name (Inter 900) and "role · source" (Inter 600, dim).

**Motion**
- Slides up 60 px with a fade on `at`. Words go from 12% to full opacity one by one between `revealFrom` and `revealTo` (follow my words when I read the quote).

**Gotchas**
- Quote exactly; shorten only with "…" (fact-check notes). Name + role + source as text, never an avatar or photo of the person (series rule).
- A card that was there before the quote (a plan card) shrinks and lifts out of the way; check that any sticky note added later doesn't land on its stamp.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
