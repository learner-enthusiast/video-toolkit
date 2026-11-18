# DataPlanPhone

**Purpose:** the mobile-data analogy: a plan is sold in GB, not in visits, because visits differ in size.

**Props:** `strikeAt` ("100 websites/day" struck through), `pillAt` ("2 GB/day" pill), `visits` ([{at, kind: text | movie, size, drain 0–1}]), `rect`, `at`, `out`. `mini`: only the "2 GB/day" pill (callback beside the head).

**Look**
- Generic phone (near-black bezel) with a status bar. A dim grey plan card "100 websites/day"; an orange status-bar pill "2 GB/day".
- A horizontal data bar under the status bar (orange = left).
- Two visit rows: a text page (lines icon, "2 MB") and a movie (play icon, "2 GB"), each with the same small tag "1 visit".

**Motion**
- Strike draws left to right (~8 frames), the card dims; the pill pops in its place.
- Text visit: the bar loses a sliver. Movie visit: the bar drains almost fully (ease-in-out ~20 frames) while the size counts up.
- The two "1 visit" tags pulse together on "one visit".

**Gotchas**
- No carrier names or logos; generic UI only.
- Keep the sliver visible (≥ 4 px) even though 2 MB / 2 GB is 0.1%.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
