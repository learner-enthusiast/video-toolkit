---
code: components/code/brand3/TimerRing/TimerRing.tsx
preview: components/code/brand3/TimerRing/preview.png
props: "from, at, size, out"
variants: "any start value"
last_used: "—"
---
# TimerRing

**Purpose:** a countdown for "in 60 seconds" style promises.

**Props:** `from` (seconds), `at`, `size`, `out`.

**Look**
- A thick gradient ring on a `track` circle, the number big in mono, "SEC" under it.

**Motion**
- Counts one per second from `at`; the arc eases to each new value and the number bumps.
- Exit: fade over 8 frames.

**Gotchas**
- It runs in real time: place it only where the countdown is honest.
- Two rings on one frame would share a gradient id.

## Code

Saved: `components/code/brand3/TimerRing/TimerRing.tsx` (preview: `preview.png`, rendered in Brand 3). A Brand 3 signature piece: import `shared/brand3/TimerRing/TimerRing`. If another brand needs it, move its folder up to the shared library, next to the other shared components; never copy. Brand values come from `components/code/theme.ts`.

- Code props: from, at, size, out.
- New for the three-brand setup; not yet used in a finished video.
