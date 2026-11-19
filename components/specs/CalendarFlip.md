---
code: components/code/CalendarFlip/CalendarFlip.tsx
preview: components/code/CalendarFlip/preview.png
props: "days [{label, at}], files string[], forgetAt?, forgetText?, sub?, again?, w?"
variants: "with/without a closing warning pill"
last_used: Graphify
---
# CalendarFlip

**Purpose:** repeated work across days or sessions: each day flips in on its spoken word and the same stack of items slides in again under it, greyer each time ("same files, read again").

**Props:** `days` (label + frame), `files` (the repeated items), `sub` (line under the day name, default "new session"), `again` (pill under repeats, default "read again"), `forgetAt` / `forgetText` (orange warning + pill that lands at the end), `w` (card width, default 972).

**Look**
- Day cards: orange header band with the day in Inter 900 white, a dim sub line. Items as small white mono chips; the last day's chips turn warm grey.
- Warning: the brand WarnMark + an outline pill, centred below.

**Motion**
- Each day flips down from the top edge (rotateX −85° → 0, spring). Chips enter staggered 4 frames. Pills pop.

**Gotchas**
- 3 columns of 292 px at 22 px mono fit "CheckoutController"; longer names need a narrower font or fewer columns.

## Code

Saved: `components/code/CalendarFlip/CalendarFlip.tsx` (preview: `preview.png`).
