---
code: components/code/PhoneStrip/PhoneStrip.tsx
preview: components/code/PhoneStrip/preview.png
props: "w, compact, nodes [{label,icon,at?}], calls [{label,at,deadAt?,hangAt?}] ×2, flow [{call,dir,from,to}], slot {at,label,fillAt?,fillLabel?,out?}, at, out"
variants: "full/compact, live/dead/hung-up calls, server slot (dashed → filled)"
last_used: system-design-of-ai/06-cancellation
---
# PhoneStrip

**Purpose:** the "two phone calls" metaphor for a server between a client and an upstream (user ☎ server ☎ model). Each call can be live (orange) or dead (grey), and either can be hung up with an animation. A recurring through-line: it returns in later beats (timeline, fix replay, recap) so the viewer never has to relearn it.

**Props:** `nodes` (three labels, default User / Server / Model, optional logo per node), `calls` (two: `{label, at, deadAt?, hangAt?}`; label e.g. "call 1"), `flow` (optional packets: `{call, dir, from, to}` frame ranges for words travelling along a call), `compact` (one-row height for sharing a card), `at`, `out`.

**Look**
- Three nodes in a row on the brand grid: white tiles (2 px border, brand radius) with a generic line icon (user, server, chip/bot) and an Inter 800 label. Logos only for real products.
- Between them, two "call" lines drawn as a phone cord (a gentle wave) with a small handset glyph in the middle and a pill label ("call 1", "call 2").
- Live call: orange cord, orange handset, small pulsing orange dots travelling along it. Dead call: cord dims to warm grey, dashed, handset tilts off its cradle, a small orange warning mark if the brief wants "bad".

**Motion**
- Nodes pop in left to right; each cord draws itself (stroke-dashoffset, ease-in-out ~12 frames) on its call's word.
- Hang up (`hangAt`): the handset lifts and drops (spring), the cord greys and goes dashed over ~8 frames, packets on it stop. `deadAt` without `hangAt` just greys it.
- Packets: orange dots along the cord, eased, staggered 4–6 frames.

**Sound:** `pop` per call that connects, `stamp-thud` (low gain) on a hang-up.

**Gotchas**
- Keep it ≤ 260 px tall in `compact` so a timeline or code card fits under it in the same FULL card.
- Labels ≤ 10 chars; the explanation lives in captions.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/PhoneStrip/PhoneStrip.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`; glyphs (server, user, handset, chip, warning) from `glyphs.tsx`.

- Code props: w, compact, nodes [{label,icon,at?}], calls [{label,at,deadAt?,hangAt?}] ×2, flow [{call,dir,from,to}], slot {at,label,fillAt?,fillLabel?,out?}, at, out.
- First built and rendered in `system-design-of-ai/06-cancellation`.
