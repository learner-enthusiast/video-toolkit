---
code: components/code/ErrorTriage/ErrorTriage.tsx
preview: components/code/ErrorTriage/preview.png
props: "at, items ({code, lane, at}), lanes ({label, tone, note, at}), kicker, title"
variants: "none"
last_used: system-design-of-ai/07-provider-failover
---
# ErrorTriage

**Purpose:** classify errors before retrying: some can succeed later, some never will.

**Props:** `at`, `items` (`{code, lane, at}`), `lanes` (`{label, tone, note?}`; tone `orange` | `dim`), `out`.

**Look**
- A sorter box at the top ("error?"), two lanes below: an orange lane (e.g. "Retry ×2 · random delay") and a dim grey lane ("Never retry").
- Status codes are mono pills (JetBrains Mono) that drop from the sorter into their lane.
- Optional small tag on a lane (e.g. "Retry-After").

**Motion**
- Each code pill pops into the sorter on its `at`, then slides down its lane with ease-in-out.
- Orange-lane pills land scattered (seeded small delays) to echo jitter.

**Gotchas**
- Codes are text in mono; never style them as fake logos.

## Code

`components/code/ErrorTriage/ErrorTriage.tsx` (saved from `system-design-of-ai/07-provider-failover`). Building blocks: `../ProviderNode/ProviderNode` (card, packet, line), `XMark`/`TickMark`/`WarnMark` from `../glyphs`, `tween`/`shake` from `../anim`.
