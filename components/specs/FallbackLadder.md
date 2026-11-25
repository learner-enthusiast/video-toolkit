---
code: components/code/FallbackLadder/FallbackLadder.tsx
preview: components/code/FallbackLadder/preview.png
props: "rungs ({label, sub, logos, icon, at, failAt}), dropAt, landAt, x, y, w, rh, gap"
variants: "none"
last_used: system-design-of-ai/07-provider-failover
---
# FallbackLadder

**Purpose:** show a fallback chain as an order of attempts, ending in a human.

**Props:** `at`, `rungs` (`{label, sub, logos, at, dim?}`), `failUntil` (index of the last failing rung), `landAt` (frame the request lands on the answering rung), `out`.

**Look**
- Rungs are full-width white cards stacked top to bottom with a thin connector down the left; each card has its logo(s), a bold label and a small sub-line.
- A failed rung is dimmed to warm grey with a small ✕; the answering rung gets an orange ring.
- The last rung is the human: a generic avatar + a "Manual review" pill that glows orange when active.

**Motion**
- Rungs enter top-down, staggered 4–6 frames, by spring.
- The request (orange packet) drops rung to rung with ease-in-out, pausing ~6 frames on each failing rung before the ✕ lands.
- Exit: fade with the scene.

**Gotchas**
- Logos keep official colours; on the dim state lower opacity, never desaturate or recolour.
- Four rungs fit a 970 px scene at ~170 px each with 24 px gaps.

## Code

`components/code/FallbackLadder/FallbackLadder.tsx` (saved from `system-design-of-ai/07-provider-failover`). Building blocks: `../ProviderNode/ProviderNode` (card, packet, line), `XMark`/`TickMark`/`WarnMark` from `../glyphs`, `tween`/`shake` from `../anim`.
