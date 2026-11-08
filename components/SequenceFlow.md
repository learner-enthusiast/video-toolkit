# SequenceFlow

**Purpose:** a numbered protocol walkthrough (OIDC login steps 0–9, the MCP agent flow) as a sequence diagram that builds one step per spoken "Step N".

**Props:** `lanes` ([{id, label, sub?, logo?}], 2–3 columns), `steps` ([{n, from, to (lane ids; from === to = a self-step), label, chips?: [{text, at, hot?}], at, note?}]), `window` (how many recent steps stay fully visible, default 3), `counter` ({total: 9} or null), `out`, `rect`.

**Look**
- Lanes are header boxes along the top (white, 2 px border, brand radius; label in Inter 700 34 px, `sub` in 26 px dim, optional LogoTile 72 px). A dashed 2 px warm-grey lifeline hangs from each.
- A step is a horizontal arrow (2.5 px near-black, arrowhead) between lifelines with a round step badge (orange, white Inter 800 number) at its start, the label above the arrow in Inter 600 30 px, chips under it.
- A self-step (`from === to`) is a small rounded loop on the lane with the label to its side.
- Chips: JetBrains Mono 26–28 px pills (2 px border, full radius); `hot` chips sit on the orange block (white text), e.g. PKCE.
- The current step is full colour; steps older than `window` dim to warm grey (opacity 0.4) and the list scrolls up so the newest step stays in the lower half.
- Counter (top-right, inside the card): "Step 3 / 9" in Inter 700 30 px, the number in orange.

**Motion**
- Lanes pop in at their own `at` (or all at the first step), staggered 5 frames; lifelines draw down over 12 frames.
- `step.at`: badge pops, the arrow draws from `from` to `to` (eased, 10 frames), an orange packet dot travels along it once, the label rises 12 px. Chips pop at their own `at`, staggered ≥ 4 frames.
- Scroll: a spring (`springs.layout`) on the list's y when a new step needs room.
- Counter flips to the new number with a 6-frame roll.
- Exit at `out`: steps fade staggered 3 frames, lanes last.

**Gotchas**
- Step rows are ~150 px tall with chips; a 972 px-tall card fits about 5. Scroll rather than shrink text.
- Labels ≤ 26 characters; long wording goes into the caption, not the diagram.
- One SequenceFlow instance per scene; split 0–9 across scenes by passing the same lanes and a `steps` slice, so the lanes never jump.
