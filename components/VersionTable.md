# VersionTable

**Purpose:** PASETO's four versions, built row by row on the spoken words.

**Props:** `at`, `out`, `rows` ([{v, suite, status, tone: 'dim'|'plain'|'orange', note?, at, statusAt}]), `rect`.

**Look**
- Title "4 versions" (Instrument Serif Italic, orange, 72 px).
- Each row a white card, 2 px border, brand radius: left a version badge (`v1`… in JetBrains Mono 700, 56 px), middle the cipher suite in mono 34 px on its own line (`Ed25519 + XChaCha20 + BLAKE2b` must fit 972 wide, wrap after `+` if not), right the status pill.
- v1: whole row dims to warm grey, status "deprecated" + orange WarnMark.
- v2: status "still fine", side note "Piyush uses this" (Inter 600 dim with a small arrow).
- v3: status "NIST · compliance".
- v4: row border and badge orange, status pill "USE THIS" orange filled; row scales 1.03.

**Motion:** row slides in from the left on its version word; status pops on its status word; stagger ≥ 4 frames. Exit: fade + lift.

**Gotchas:** at 1.5x each row is on screen alone for ~2 s: status text ≤ 2 words.
