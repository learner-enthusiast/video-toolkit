# CheckCard

**Purpose:** a résumé-style card whose rows tick off fast, then a big "?" lands ("internships → production apps → developer → ?").

**Props:** `title`, `rows` (text, `at`), `question` (default "?"), `questionAt`, `rect`, `out`.

**Look**
- White card (2 px `#1A1A1A` border, brand radius, soft shadow) with a serif Instrument Serif Italic orange title and 3–4 rows in Inter 700 ~40 px, each with an empty 36 px check box on the left.
- A tick is an orange stroke drawn inside the box (stroke-dashoffset); a ticked row's text stays near-black, un-ticked rows are dim `#8A857C`.
- The "?" is Instrument Serif Italic, orange, ~320 px, centred over the lower half.

**Motion**
- Rows stagger in 4–6 frames apart (spring); each tick draws in ~6 frames on its spoken word with a quiet tick SFX. The "?" scales 1.4 → 1 with the Stamp spring and a 2 px shake; rows dim to 60% beneath it.
- Exit: whole card fades and slides up.

**Gotchas**
- Rows follow the spoken order: internships, production applications, developer. Keep texts ≤ 24 characters.
- No emojis, no green ticks: the tick is orange (`brand.md`).
