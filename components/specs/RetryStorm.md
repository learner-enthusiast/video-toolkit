---
code: components/code/RetryStorm/RetryStorm.tsx
preview: components/code/RetryStorm/preview.png
props: "at, out, nodeLogo, nodeLabel, scatterAt, waveEvery, waves, dimEnd"
variants: "none"
last_used: system-design-of-ai/07-provider-failover
---
# RetryStorm

**Purpose:** show why synchronized retries make an outage worse (thundering herd), and the jittered fix, on the same picture.

**Props:** `at`, `node` (label + optional logo), `waves` (number of retry waves), `mode` (`lockstep` | `jitter`), `scatterAt` (frame the lockstep turns into jitter), `out`.

**Look**
- Many small clients on the left (simple app glyphs in a column grid), one provider node on the right (white card, 2 px border, logo).
- Packets are small orange rounded squares. In `lockstep` every client fires on the same frame, so packets travel as one vertical wall; in `jitter` each packet gets a seeded random delay and they arrive as a light drizzle.
- Each lockstep wave that hits the node shakes it and dims it a step (grey ✕ badge after the last wave); jitter hits leave it steady.

**Motion**
- Waves are spaced ~18 frames; packets travel with ease-in-out, never linear.
- At `scatterAt` the waves stop and the jittered stream starts; stagger by seeded offsets (deterministic per render).
- Exit: fade with the scene.

**Gotchas**
- Seed the jitter (`random('jitter-' + i)`), or frames differ between render workers.
- Keep at most ~40 packets on screen; more reads as noise at 9:16.

## Code

`components/code/RetryStorm/RetryStorm.tsx` (saved from `system-design-of-ai/07-provider-failover`). Building blocks: `../ProviderNode/ProviderNode` (card, packet, line), `XMark`/`TickMark`/`WarnMark` from `../glyphs`, `tween`/`shake` from `../anim`.
