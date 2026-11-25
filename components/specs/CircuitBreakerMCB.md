---
code: components/code/CircuitBreakerMCB/CircuitBreakerMCB.tsx
preview: components/code/CircuitBreakerMCB/preview.png
props: "at, tripAt, failAts, w"
variants: "none"
last_used: system-design-of-ai/07-provider-failover
---
# CircuitBreakerMCB

**Purpose:** explain a circuit breaker with the switch everyone has at home (India: MCB in the distribution box).

**Props:** `at`, `failAts` (frames of the failure ✕ marks), `tripAt`, `rerouteAt`, `label` (provider), `out`.

**Look**
- A generic white MCB module (no brand): rounded body, 2 px near-black border, a lever in a slot, a small "ON / OFF" legend, an orange window.
- Beside it, the provider node with its logo; a request path runs through the switch.
- Failure ✕ marks: small dim grey circles with ✕, stacked under the switch.

**Motion**
- ✕ marks pop in on `failAts` (staggered, one per failure).
- At `tripAt` the lever springs down (overshoot allowed), the window turns grey, and the path behind the switch dims to warm grey with a dashed stroke; a stamp-thud SFX lands here.
- At `rerouteAt` an orange packet takes the alternate path (drawn with a self-drawing line) to the backup.

**Gotchas**
- "Bad" is dim grey + orange warning, never red (`brand.md`).
- Keep the lever travel ≥ 60 px so the trip reads on a phone.

## Code

`components/code/CircuitBreakerMCB/CircuitBreakerMCB.tsx` (saved from `system-design-of-ai/07-provider-failover`). Building blocks: `../ProviderNode/ProviderNode` (card, packet, line), `XMark`/`TickMark`/`WarnMark` from `../glyphs`, `tween`/`shake` from `../anim`.
