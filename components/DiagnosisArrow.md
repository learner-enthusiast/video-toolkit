# DiagnosisArrow

**Purpose:** an arrow that loops back from a symptom to its cause (faithfulness high + answer wrong → Retrieval).

**Props:** `from`, `to`, `label`, `at`, `out`.

**Look**
- A curved orange arrow (4 px) looping back with a label pill on the target ("Retrieval"), target gets an orange ring pulse.

**Motion**
- Draws with stroke-dashoffset (~15 frames), target pulses twice.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
