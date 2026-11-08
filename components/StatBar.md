# StatBar

**Purpose:** a survey number that rises year over year (Stack Overflow 2024 → 2025).

**Props:** `bars` (`[{label, value, tone, at}]`), `max`, `deltaAt`, `deltaText`, `source` (logo + label), `at`, `out`.

**Look**
- Vertical bars on a faint track with a shared baseline; old year warm grey, new year orange; value labels in Inter 900 above (tabular figures); year labels below.
- Delta: an orange curved arrow between the bar tops with a "+17 pts" solid `Tag`.
- Source: official logo at the top-left of the card with the survey name.

**Motion**
- Bars grow from 0 with ease-out ~20 frames while their numbers count; the new bar grows on its spoken number.
- Arrow draws itself, tag pops.

**Gotchas**
- Bars share one max so heights are honest; no red/green.
