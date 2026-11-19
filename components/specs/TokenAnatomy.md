# TokenAnatomy

**Purpose:** a token string splits at its dots into labelled part cards, and the claims pop in as they are said. Reusable: Part 2 (PASETO) extends it to 4 parts.

**Props:** `token` (string), `parts` ([{label, color, body (rows), at}]) — any count (3 for JWT, 4 for PASETO), `splitAt`, `claims` ([{key, value, note, at}]) shown in the payload card, `formula` ({text, at}) in the signature card, `lockAt` (key-in-server icon), `focus` (index of the part in focus, others dim), `rect`, `out`.

**Look**
- Token line on top in JetBrains Mono ≥ 34 px, the parts tinted (header near-black, payload orange, signature warm grey); dots in orange.
- Part cards stacked vertically: label in Inter 800 caps (HEADER / PAYLOAD / SIGNATURE), body in mono ≥ 34 px.
- Claim rows: `"sub": "42"` plus a dim Inter note ("who you are"); the newest row gets an orange block behind its key.
- Formula card: `HMAC-SHA256(header + "." + payload, SECRET)` wrapped to 2–3 lines, with a small server icon holding a locked key icon (orange key).

**Motion**
- Split: the token's parts fly down into their cards (spring), staggered 5 frames, on `splitAt`.
- Each claim row slides in from the left 24 px on its spoken word.
- `focus` dims the non-focused cards to 0.45 opacity (spring).
- Exit: fade + lift 8 frames.

**Gotchas**
- Card layout is computed from `parts.length`, never hard-coded to 3.
- Five claim rows + header + formula don't fit at once in a 972x971 card: collapse the header card to one line when the payload opens, and the payload to a summary when the signature opens.
