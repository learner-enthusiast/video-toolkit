# TextMorph

**Purpose:** a phrase reshuffles into another ("Web Developer" → strike-through → "Software Engineer"; "WEB DEVELOPMENT COHORT" → letters reshuffle → "SOFTWARE DEVELOPMENT COHORT").

**Props:** `from`, `to`, `mode` ('strike' | 'shuffle'), `at`, `dark`, `size`, `highlight` (words to put on the orange block), `rect`, `out`.

**Look**
- Strike mode: the old text in dim `#8A857C` Inter 800 with an orange line drawn through it; the new text in Instrument Serif Italic orange below/over it, large.
- Shuffle mode: uppercase Inter 900 letter tiles; shared letters stay, the others hop to their new slots (spring, 2–4 frame stagger), unmatched tiles fade in/out. Dark style (`#0D0D0D`, white text, orange accent) for the punch.

**Motion**
- Starts on the spoken trigger word; ~20–28 frames total, spring or ease-in-out only; a soft thud on the settle.
- The finished phrase holds, then exits with the beat.

**Gotchas**
- Shuffle needs ≥ 70% matched letters to read as a reshuffle: here "WEB" → "SOFTWARE" shares few, so swap the word as tiles while the common words (DEVELOPMENT COHORT) stay put.
- Keep the text on the 5% grid and inside the safe margin; never cover the face in HEAD.
