# DecoderReveal

**Purpose:** a JWT pasted into a generic decoder box, used twice: the hook teases that the payload is readable (flash, then blur), and the interview answer reveals it fully. One component, two states.

**Props:** `state` (`tease` | `reveal`), `token` (string), `payload` (rows `[key, value]`), `pasteAt`, `noAt`, `yesAt`, `flashAt`, `blurAt` (tease), `revealAt` (reveal), `rows` (reveal: per-row `at`), `stamp` ({text, at}), `tags` ([{label, at}]), `rect`, `out`.

**Look**
- A white card (2 px border, radius 14, brand shadow) titled "JWT decoder" in Inter 700 with a generic line icon; never jwt.io's logo, colours or layout.
- Top field: the token in JetBrains Mono ≥ 34 px, wrapped, the three parts tinted near-black / orange / warm grey at the dots.
- Bottom field: the payload JSON in mono ≥ 34 px.
- `tease`: a big orange "?" in Instrument Serif Italic over the bottom field; NO chip (warm grey fill, near-black text) then YES chip (orange fill, white text) on the same spot.
- `reveal`: payload sharp; `"role":"user"` row ready for TamperCrack to edit.

**Motion**
- Paste: the token types in fast (2–3 chars/frame) with a caret, ending on `pasteAt` + ~12 frames. On frame 0 of the video the token and "?" are already on screen (hook rule): pass `pasteAt` < 0 to start pre-built.
- NO chip pops (spring) on `noAt`; flips (rotateX 180° spring) to YES on `yesAt`.
- Tease flash: blur 14 px → 0 on `flashAt` (8 frames), hold ~0.8 s, blur back to 14 px on `blurAt`.
- Reveal: blur 14 → 0 on `revealAt`; rows highlight (orange block behind the value) on their spoken word.
- Exit: fade + lift 8 frames.

**Gotchas**
- Build it reusable: the reveal state is re-mounted later with the same token, so the two beats read as the same box.
- Mono text stays ≥ 34 px on a 1080-wide frame; wrap the token rather than shrinking it.
