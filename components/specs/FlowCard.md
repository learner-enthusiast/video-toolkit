# FlowCard

**Purpose:** a two-line ASCII-style request flow (login, then an authenticated request) with a check landing on "200".

**Props:** `lines` ([{steps: [string], at: [frame per step]}]), `checkAt`, `tag` ({label, at}), `lb` ({at, server, passAt}) optional, `rect`, `out`.

**Look**
- A white code-style card; each line is a vertical stack of mono chips (≥ 34 px) joined by orange `──►` arrows, since one horizontal line can't fit 972 px.
- Final step `✓ 200` in an orange chip with a white tick.
- Optional mini load balancer → Server 3 strip below, passing with an orange tick.
- Tag pill (e.g. "Stores nothing").

**Motion**
- Each chip pops on its spoken word; arrows draw between chips (stroke) as the next one lands.
- An orange packet dot rides the arrows.
- Exit: fade 8 frames.
