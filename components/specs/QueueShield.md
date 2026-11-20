---
code: components/code/QueueShield/QueueShield.tsx
preview: components/code/QueueShield/preview.png
props: "QueueShield {x,y,w,h,at,out,shieldAt,label,tickets,floodAt,floodFrom,bypassAt,bypassFrom,bypassTo}"
variants: "flat queue → shield morph, flood absorbed, bypass arcs"
last_used: system-design-of-ai/10-batch-inference
---
# QueueShield

**Purpose:** a queue drawn as a shield: an orange stack of tickets standing in front of a "Your servers" box and absorbing a flood of incoming requests. It shows what a queue protects. It can then be bypassed: arrows fly over it to a node behind (a provider limit, a tank), so the viewer sees what the queue does *not* protect.

**Props:** `x`, `y`, `w`, `h` (shield rect), `tickets` (count stacked, default 6), `serversLabel` ("Your servers"), `at` (shield forms from the flat queue), `floodAt` (dots hit the shield face and stop), `absorb` (0..1, dots slide into the stack), `tag` ({text, at}, e.g. "already paid ✓"), `bypassAt` (arrows arc over the top toward `bypassTo` {x, y}), `dimAt`, `out`.

**Look**
- Shield outline: 2 px near-black, brand radius on the corners, a pointed bottom; fill off-white with the ticket stack inside (orange tickets, 2 px border, slight offset per ticket).
- "Your servers": white tile behind the shield, 2 px border, generic server line icon, Inter 800 label; "already paid ✓" as an orange Tag.
- Flood dots: small near-black dots; on hit they turn orange and slot into the stack.
- Bypass arrows: thick orange arcs drawn over the shield (stroke-dashoffset), arrowheads at the target.

**Motion**
- Form: the flat queue row folds up into the shield (spring, ~14 frames).
- Flood: dots stream in eased, stop at the face with a tiny bounce; tickets nudge (4-frame stagger).
- Bypass: each arc draws ease-in-out ~12 frames, staggered 4–6 frames; the shield stays lit (it still guards the servers).
- Everything exits with a fade on `out`.

**Sound:** `pop` on form, `soft-pop` on the tag, `whoosh` on the bypass arcs.

**Gotchas**
- Keep it in the master-diagram coordinates so it can replace the "Queue" node in place.
- No red/green; bypass is shown by arrows, not by turning the shield grey.
- Triggers on spoken-word frames (`at(phrase)`); every element has an exit.

## Code

Saved: `components/code/QueueShield/QueueShield.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: QueueShield {x,y,w,h,at,out,shieldAt,label,tickets,floodAt,floodFrom,bypassAt,bypassFrom,bypassTo}.
- First built and rendered in `system-design-of-ai/10-batch-inference`.
