# Timeline

**Purpose:** a dated line that draws from a past year to "today", for "this has been around since…" moments.

**Props:** `stops` (label, sublabel, `at`), `orientation` (horizontal | vertical), `rect`, `out`.

**Look**
- One 3 px line in text color with round caps; tick marks at each stop.
- Year in the headline font (serif italic, accent) above the tick, sublabel in body font below.
- The last stop gets an accent block behind its key word (e.g. "#1").
- A travelling dot in the accent color, about 18 px, with a soft glow.

**Motion**
- The line draws itself (stroke-dashoffset, ease-in-out) from the first stop's word to the last stop's word.
- Each stop's tick and labels pop in with a spring when the dot reaches it, on its spoken word.
- The dot rides the drawn tip; it never runs ahead of the line.
- Exit: line and labels fade with a slight lift before `out`.

**Gotchas**
- Space stops by meaning, not years to scale (1970 → today would leave a huge gap).
- Keep labels ≤ 18 chars so they fit at phone width.
