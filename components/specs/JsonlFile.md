---
code: components/code/JsonlFile/JsonlFile.tsx
preview: components/code/JsonlFile/preview.png
props: "JsonlFile {at,out,stackAt,counterAt,dropAt,chipAt,fileName,idPrefix,counter,logo,lane,chip} · FileIcon {w,label}"
variants: "lines stacking, counter, file fan dropping into a logo or server, completion_window chip"
last_used: system-design-of-ai/10-batch-inference
---
# JsonlFile

**Purpose:** how a batch job is packed: request lines stack into a file (one line per user, each tagged `custom_id`), a counter splits the work into files, and the files drop into a provider logo with a `completion_window: "24h"` chip.

**Props:** `x`, `y`, `w`, `h`, `lines` (sample strings, e.g. `{"custom_id": "user_000001", "body": {...}}`), `stackAt` (lines start dropping in), `counter` ({text, at}, e.g. "50,000 lines per file → 20 files"), `files` (count shown as a fan of file icons), `dropAt` (files fall into the logo), `logo` (official file from `icons/logos/`), `chip` ({text, at}), `at`, `out`.

**Look**
- A white file card (2 px border, brand radius, folded corner) titled `requests.jsonl` in JetBrains Mono; lines in mono 22–26 px, `custom_id` value in orange.
- Counter: Inter 900 numerals with an orange arrow.
- Files: small file icons fanned in a row; the provider logo on a white tile; the chip as a mono pill with an orange border.

**Motion**
- Lines drop in one by one (spring, 4–6 frame stagger), the file grows; after ~6 lines it compresses into "…".
- The file duplicates into the fan (stagger 3–4 frames), then the fan arcs down into the logo (ease-in-out ~16 frames) and the chip pops.
- Exit with a fade on `out`.

**Sound:** `typing-tick` on line drops (max every 4 frames), `tick` on the counter, `pop` on the chip.

**Gotchas**
- Real field names (`custom_id`, `body`, `completion_window`) in mono, exactly spelt.
- Mono text ≥ 22 px in a 972 px card; never cut a line, ellipsize instead.

## Code

Saved: `components/code/JsonlFile/JsonlFile.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: JsonlFile {at,out,stackAt,counterAt,dropAt,chipAt,fileName,idPrefix,counter,logo,lane,chip} · FileIcon {w,label}.
- First built and rendered in `system-design-of-ai/10-batch-inference`.
