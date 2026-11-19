# PriceTag

**Purpose:** one price chip that stays the same object through a story (cache vs database value, stale vs correct).

**Props:** `value` (₹, Indian format), `state` (correct | stale | neutral), `flipTo` {value, at}, `label` (e.g. `DB`, `Redis`, "Last known price"), `size` (full | mini), `rect`, `at`, `out`.

**Look**
- Black text on a white chip, Inter 800, tabular nums, ₹ with a thin space. Brand radius, 2 px border.
- correct: orange border. stale: red strike-through over the value + a small red **Stale** stamp at the corner. neutral: near-black border.
- mini: ~40% size for server rings and avatar rows.

**Motion**
- Flip: the old value rolls up and out while the new one rolls in (split-flap feel, ~10 frames, ease-in-out) on the spoken number.
- Stale: the strike draws left to right (~8 frames), then the stamp lands (`Stamp` motion).

**Gotchas**
- Indian grouping everywhere (₹79,999; 5,00,000). Format from one helper, never typed by hand per scene.
