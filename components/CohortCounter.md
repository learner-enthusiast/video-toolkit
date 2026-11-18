# CohortCounter

**Purpose:** a running "×N" tally of how many times the presenter paid (hook ×1, spiral ×2 → ×3 → ×4, finale ×5).

**Props:** `value`, `prev`, `at` (frame the value changes), `corner` ('tr' | 'tl'), `dark`, `sfx` ('tick' | 'sad'), `label` (default "cohorts bought"), `out`.

**Look**
- A pill in the card's top-right corner: 2 px `#1A1A1A` border (white on dark), brand radius, "×" in dim `#8A857C`, the number in Inter 900 ~64 px orange, tabular figures; label under it in Inter 600 ~20 px dim.
- The number is the only orange thing in it. No red/green; the sad ×5 is shown by a dim-grey wobble, not a colour change.

**Motion**
- Value change: the old digit slides up and out, the new one springs in from below (stiff spring, small overshoot), pill scale bump 1 → 1.06 → 1 on the tick SFX (`sfx-counter-tick.wav`, low volume).
- ×5 only: after the bump the pill droops 4° and sags 6 px (soft ease), with `sfx-sad-trombone.wav` at low volume.
- Enters with the scene (popIn), exits with it; never loops.

**Gotchas**
- Trigger on the spoken word (`at("enrolled")`), not a fixed time; the number must match what the presenter says (a script "four" may be spoken "all four").
- Keep the top-right 420×80 of the card free of other tags while the counter is on (`ReelSplit.md` corner pill rule); in HEAD draw it on the wall box, never over the face.
