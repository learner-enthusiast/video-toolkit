# StackBurst

**Purpose:** "fifty sites, one reused password, one leak, everything's gone": a stack of login forms that all share one password, one cracks, and the leak takes the rest down with it.

**Props:** `count` (cards drawn, default 7; a "×50" tag stands in for the rest), `password` (shown masked, e.g. `••••••••`), `stackAt`, `reuseAt`, `leakAt`, `goneAt`, `out`, `rect`.

**Look**
- Generic login cards (white, 2 px border, brand radius, shadow), ~420×260 at full size, fanned in a loose stack (each card offset 34 px down-right, rotated −4°…+4°, seeded, never random per frame). Each card: a dim site label (`site-01` … no real brands), a username field and a password field.
- The shared password field is one orange-outlined pill repeated on every card, so "reused" reads at a glance.
- Leak: the front card gets an orange crack (a jagged 4 px path drawn across it) and a WarnMark; the password pill pops out of it as a small orange chip.
- Gone: every other card dims to warm grey (opacity 0.45, desaturated), and one orange WarnMark lands at the stack's top-right. No red.
- "×50" tag (Tag.md style) at the stack's bottom-right.

**Motion**
- `stackAt`: cards drop in one by one, staggered 4 frames, spring from 40 px above.
- `reuseAt`: the password pills light orange together, staggered 2 frames back to front.
- `leakAt`: crack draws over 8 frames (stroke-dashoffset), a 2 px / 4 frame shake, the chip springs out 60 px up-right.
- `goneAt`: the dim sweeps back to front, staggered 3 frames; the warning lands with `pop`.
- Exit at `out`: cards slide down 30 px and fade, staggered 3 frames.

**Gotchas**
- Keep the stack inside the card's free rect with ≥ 48 px padding; the fan offset grows with `count`, so lay it out from the last card's rect.
- Field text ≥ 30 px so it reads at phone width.
