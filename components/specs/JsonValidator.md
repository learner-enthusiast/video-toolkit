---
code: components/code/JsonValidator/JsonValidator.tsx
preview: components/code/JsonValidator/preview.png
props: "at, bad, good, rejectAt, rerunAt, passAt, gateLabel, rerunLabel"
variants: "none"
last_used: system-design-of-ai/07-provider-failover
---
# JsonValidator

**Purpose:** validate model output before acting on it; never act on a partial response.

**Props:** `at`, `bad` (string, e.g. `{ "decision": "appr`), `good` (string), `rejectAt`, `rerunAt`, `passAt`, `out`.

**Look**
- A check gate in the middle (two posts, a bar, a small "valid JSON?" label).
- JSON cards are CodeCard-style mono blocks. The bad one ends with a torn edge.
- A simple bin under the gate (line style); a "rerun on backup" tag on the second card.

**Motion**
- The bad card slides into the gate, the bar flashes dim grey with an orange ⚠, the card drops into the bin (spring).
- At `rerunAt` the full JSON types in; at `passAt` it passes through and an orange tick lands.

**Gotchas**
- Keep the JSON text short enough for one line at ≥ 30 px on 9:16.

## Code

`components/code/JsonValidator/JsonValidator.tsx` (saved from `system-design-of-ai/07-provider-failover`). Building blocks: `../ProviderNode/ProviderNode` (card, packet, line), `XMark`/`TickMark`/`WarnMark` from `../glyphs`, `tween`/`shake` from `../anim`.
