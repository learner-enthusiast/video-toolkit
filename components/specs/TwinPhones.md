# TwinPhones

**Purpose:** two generic phones side by side doing the same thing at the same moment (a race condition, two users, A/B).

**Props:** `typed` (text), `typeAt`, `result` (text + tone), `resultAt`, `stamp` (text, `at`), `rect`, `out`.

**Look**
- Two simple phone outlines (rounded rect, 2 px near-black border, notch bar), no real app UI or logos. Inside each: a generic input field with a label and a result line.
- The typed text is in JetBrains Mono. Optional user labels above each phone ("user A", "user B") in dim Inter.

**Motion**
- Both phones pop in staggered 4 frames, then type the same text in sync (seeded per-character jitter, identical on both).
- Results appear on both on the same frame with a spring.
- The `Stamp` lands across the gap between the phones, overlapping both slightly, never over my face.

**Gotchas**
- Keep the phones' inner text ≥ 32 px so it reads at phone width; two phones on a 970 px card are ~400 px wide each.
