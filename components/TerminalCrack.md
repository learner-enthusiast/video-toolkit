# TerminalCrack

**Purpose:** cracking a weak HS256 secret offline, then the fix (a 256-bit random key).

**Props:** `cmd` (`hashcat -m 16500 token.txt wordlist.txt`), `typeAt`, `resultAt` (`Cracked: secret`), `forgeAt` (forged-token stamp "role: admin"), `keyAt` (orange key chip "256-bit random key"), `rect`, `out`.

**Look**
- A near-black terminal card (radius 14, 2 px border, title bar with three dim dots), JetBrains Mono ≥ 34 px white; prompt `$` in orange. Command wraps to 2 lines.
- Result line `Cracked: secret` with `secret` on an orange block.
- Forged-token stamp: Stamp.md style in warm grey with an orange WarnMark, text "FORGED · role: admin".
- Key chip: orange fill, white text, key line icon.

**Motion**
- Command types at ~1.5 chars/frame on `typeAt`; a short progress bar (ease-in-out) before the result line.
- Stamp lands per Stamp.md; key chip pops (spring) as the terminal dims.
- Exit: fade 8 frames.

**Gotchas:** it's a graphic only; hashcat is never installed or run.
