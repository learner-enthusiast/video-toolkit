# TaskBudget

**Purpose:** budget the whole agent task, not each call: one orange box around the run that snaps shut when the spend hits its limit, plus a cost preview before the user presses Run.

**Props:** `limit` (₹50), `steps` (call/retry labels), `at`, `stopAt`, `previewAt`, `preview` ("This task: ~₹12"), `logos` + `stampAt` (companies that faced surprise bills), `out`.

**Look**
- Orange-bordered box (4 px, brand radius, translucent white), kicker "one agent task", step pills (ink "call", dim "retry"), and a spend bar with "₹x / ₹50" in mono. Orange pill "task budget: ₹50" on the top edge.
- Preview row: white chip "This task: ~₹12" + orange "Run ▶" button + "example" tag.
- Logos in white tiles; a dim "surprise bills" stamp UNDER the tiles, never over the marks.

**Motion**
- Steps pop every 6 frames until `stopAt`; the border thickens (snap) and an orange "STOPPED" stamp lands. Preview and logos pop on their words.

**Gotchas**
- Stamps over logos hide the official mark; keep stamps below or beside them (`brand.md`: never crop or cover logos).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
