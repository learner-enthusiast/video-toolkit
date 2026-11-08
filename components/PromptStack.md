# PromptStack

**Purpose:** a prompt box stacks its parts in order as they are spoken: Instruction → best chunk → chunks 2–5 → Question.

**Props:** `parts` (label, body, tone, `at`), `rect`, `out`.

**Look**
- One tall prompt card with a header "prompt"; each part a row block. Best chunk orange, other chunks white with grey lines, question near-black.

**Motion**
- Each block drops into the next slot with a spring when spoken; earlier blocks stay. Instruction lines reveal word by word.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
