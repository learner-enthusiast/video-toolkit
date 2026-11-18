# PrepaidMeter

**Purpose:** a per-user budget as a prepaid smart meter: a balance that each call drains, a warning at 80%, and two outcomes at zero (stop, or switch to a cheaper model).

**Props:** `balance` (₹500), `at`, `drainAt`, `warnAt`, `zeroAt`, `stopAt`, `cheaperAt`, `teaseTag` ("#5"), `out`.

**Look**
- White device panel: "PREPAID · per user" header, a #0D0D0D LCD with "BALANCE" and a big orange mono ₹ value, a pill bar under it (orange, grey below 20%), an "example" tag.
- Toast: white card, 4 px orange border, ⚠ + "80% used", slightly rotated over the device's top-right corner.
- Outcomes: "STOP" (grey fill, dim border/text) and "↓ cheaper model" (orange fill, white text, ≥ 440 px wide at 42 px) with arrows from the device; a small ink "#5" tag on the second one.

**Motion**
- From `drainAt`, "call" pills slide into the device every 7 frames (tick SFX) while the balance counts down ease-out to 20% at `warnAt`, then to 0 at `zeroAt` (LCD blinks). Arrows draw and outcome cards pop on their words.

**Gotchas**
- Numbers are illustrative: tag "example". The 80% must match what's shown even if the take says "eight percent" (captions/graphics use the intended number).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
