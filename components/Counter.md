# Counter

**Purpose:** an animated number for a result ("−3s API response time", "62%").

**Props:** `from`, `to`, `decimals`, `prefix`, `suffix`, `label`, `at`, `duration`, `tone`.

**Look**
- Big numeral in Inter 800 at 120–160 px with tabular figures (`font-variant-numeric: tabular-nums`), so the width doesn't jitter.
- Label below in dim Inter 500. Use the good tone for improvements, the bad tone for regressions.

**Motion**
- Count with an ease-out curve over about 1 s, starting on the spoken number.
- On landing: a tiny scale bump (1 → 1.04 → 1) and an optional tick SFX.
- Fade out at `out`.

**Gotchas**
- Format with a real minus sign (`−`), not a hyphen.
- The final value must equal what I say. If the script and the speech differ, follow the speech.
