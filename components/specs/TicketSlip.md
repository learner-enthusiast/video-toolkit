---
code: components/code/TicketSlip/TicketSlip.tsx
preview: components/code/TicketSlip/preview.png
props: "TicketArt {w,id,label,sub,dim,shadow} · TicketSlip {x,y,w,id,at,out,sub,morphFrom {text,at},dock {x,y,scale,at},dim}"
variants: "pop-in, morph from JSON, docked mini, dim"
last_used: system-design-of-ai/08-long-running-requests
---
# TicketSlip

**Purpose:** the "ticket number" of the async fix as a physical orange paper ticket ("#0427"). It pops in on the analogy, is born again from a server's `jobId`, and rides small in a corner as a callback, so "job ID = your ticket" sticks.

**Props:** `id` ("#0427"), `label` (small caps line, e.g. "TICKET"), `at`, `out`, `morphFrom` (`{text, at}`: starts as a mono JSON string box and morphs into the slip), `dock` (`{x, y, scale, at}`: springs to a smaller resting place), `mini` (static small version), `dim`, `x`, `y`, `w`.

**Look**
- Orange #E4572E slip, white text, 2 px near-black border, brand radius, with two half-circle notches on the sides and a dashed perforation line near the left stub.
- Id in Inter 900, label in Inter 800 caps with letter spacing; stub carries a small mono "job_0427" when morphed from JSON.
- Flat brand shadow on light scenes, none on dark.

**Motion**
- Pop-in: scale 0.7 → 1 with a slight 6° tilt settling to −3°, spring.
- Morph: the JSON box cross-fades and reshapes (width/height/radius springs) into the slip over ~12 frames.
- Dock: springs to `dock` with scale; exit fades on `out`.

**Sound:** `pop` on pop-in and morph.

**Gotchas**
- One ticket id per video; the same slip reappears, never a second number (that is the idempotency point).
- Text ≥ 40 px at full size so it reads on a phone; the docked mini only needs to be recognisable.

## Code

Saved: `components/code/TicketSlip/TicketSlip.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: TicketArt {w,id,label,sub,dim,shadow} · TicketSlip {x,y,w,id,at,out,sub,morphFrom {text,at},dock {x,y,scale,at},dim}.
- First built and rendered in `system-design-of-ai/08-long-running-requests`.
