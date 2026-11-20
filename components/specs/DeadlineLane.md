---
code: components/code/DeadlineLane/DeadlineLane.tsx
preview: components/code/DeadlineLane/preview.png
props: "DeadlineLane {at,out,runFrom,runTo,deadlineAt,peelAt,laneAt,start,deadline,deadlineNote,leftover,lane}"
variants: "progress to a deadline, leftovers peel into a fallback lane"
last_used: system-design-of-ai/10-batch-inference
---
# DeadlineLane

**Purpose:** plan for the worst case of an async job window. A progress timeline runs from a submit time ("3:45 PM submit") toward a deadline line ("8:00 AM"); at the deadline the leftover items ("312 pending") peel off into a fallback lane ("Express: real-time").

**Props:** `x`, `y`, `w`, `h`, `start` ({label}), `deadline` ({label, x}), `progressTo` (0..1 at the deadline), `runFrom`, `runTo` (progress fill frames), `deadlineAt` (line flashes), `leftover` ({label, count}), `peelAt`, `lane` ({label}), `at`, `out`.

**Look**
- Thick timeline bar (brand radius) with orange fill; start label left, deadline as a vertical near-black dashed line with a mono time pill.
- Leftover: a small stack of grey line blocks with a mono count pill and orange ⚠; fallback lane: an orange lane with a lightning-free generic "fast" chevron icon and Inter 800 label.

**Motion**
- Progress fills ease-in-out; the clock pill ticks on spoken numbers.
- At the deadline the line pulses once; leftovers lift off the bar and arc into the lane (spring, stagger 4 frames), then turn orange as they complete.
- Exit with a fade on `out`.

**Sound:** `tick` on time steps, `pop` on the deadline, `whoosh` on the peel.

**Gotchas**
- Counts are illustrative; keep them in the episode's `facts.md`.
- Never red/green.

## Code

Saved: `components/code/DeadlineLane/DeadlineLane.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: DeadlineLane {at,out,runFrom,runTo,deadlineAt,peelAt,laneAt,start,deadline,deadlineNote,leftover,lane}.
- First built and rendered in `system-design-of-ai/10-batch-inference`.
