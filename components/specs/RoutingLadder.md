---
code: components/code/RoutingLadder/RoutingLadder.tsx
preview: components/code/RoutingLadder/preview.png
props: "frameAt, rungs, active, drops, lanes, prices, laneNote, intake, out, layout"
variants: "small/big lanes, laneNote vs prices"
last_used: system-design-of-ai/05-model-routing
---
# RoutingLadder

**Purpose:** the recurring picture of model routing as a decision ladder. A request (a PullRequestCard in miniature) drops in at the top, falls through the rungs, and lands in one of two output lanes: **Small model** or **Big model**. It builds one rung per step as I name it and stays on screen across the whole fix section, so each new step is seen in the context of the earlier ones.

**Props:** `rungs` (array of `{label, sub?, chip?}` e.g. Rules "path → lane", Classifier "easy / hard" + chip "~ms", "Unsure → Big", Measure "cost per review"), `built` (number of rungs shown), `active` (index of the lit rung, or -1), `drops` (array of `{at, label, lane: 'small' | 'big', exitRung?}`: a mini PR that falls and lands in a lane, optionally decided at a given rung), `lanes` (labels, default "Small model" / "Big model"), `compact` (smaller scale when it shares the card with another visual), `at`, `out`.

**Look**
- Vertical stack inside the grid card: an intake slot at the top ("request"), then the rungs as full-width white panels (brand border/radius), numbered with step badges ①–④. The active rung has an orange 4 px outline and orange badge; built-but-inactive rungs are near-black; unbuilt rungs are dashed grey placeholders.
- Bottom: two output lanes as trays, left **Small model** (cheap, `₹5`) and right **Big model** (`₹100`), using the same Big/Small model boxes as the rest of the video (orange outline for Big, near-black for Small) so viewers learn them once.
- Mini PR: a small white pill with a PR glyph and short label ("README", "payments/charge.ts"). It turns orange when routed to Big, stays ink when routed to Small.

**Motion**
- Empty frame draws in (outline strokes, ease-in-out) when the concept is named. Each rung springs in on its step word ("Step one", "Step two"…), then becomes active; the previous one de-lights to near-black. Mini PRs fall with gravity-like ease-in, pause briefly at the deciding rung (it flashes), then slide sideways into their lane and settle with a spring. Exit: the whole ladder fades/scales down at the end of the section.

**Sound:** `pop` per new rung; `soft-pop` when a mini PR lands in a lane; `whoosh` only on the layout switch, not on drops.

**Gotchas**
- It must stay readable when another visual (a CodeCard, a TradeScale) shares the card: use `compact` and park it on one side rather than covering it.
- Never show more than two mini PRs falling at once; stagger 6–10 frames.
- Rung labels are short (≤ 16 chars); explanations belong in captions and spoken words.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/RoutingLadder/RoutingLadder.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: frameAt, rungs, active, drops, lanes, prices, laneNote, intake, out, layout.
- Any number of rungs; lane names, prices and the intake label are props (no default prices).
