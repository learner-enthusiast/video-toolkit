# Captions

**Purpose:** burned-in captions with word-by-word highlight, from the final timeline's words.

**Props:** `words` (text, start/end output frames), `mode` (16:9 | reel), `avoid` rects (bubble, lower third, bottom overlays).

**16:9 look**
- At most 2 lines, bottom center inside the safe margin, Inter 600 at about 44 px in white, with a soft dark text shadow or a translucent backing.
- The current word is in the accent color; spoken words stay white, upcoming ones about 70% white.
- Split into pages by phrase: about 42 characters per line, breaking at punctuation and pauses.

**Reel look**
- 1–3 words at a time, Inter 800 at about 80 px, centered at mid-frame between face and screen.
- Each page pops with a quick spring.

**Behaviour**
- Move up automatically when any `avoid` rect overlaps the caption band, with a smooth spring and no jumping.
- Leave no captions during the typing intro and the end card.
- Use the glossary spellings from `script.md` (pgvector, tRPC, PostgreSQL…).

**Gotchas**
- Display text follows my actual words. Only spelling or casing fixes and agreed replacements are allowed.
- Reel HEAD with a close-up portrait (face ~620 px wide, chin at y≈1450–1540): a lower-third band lands on the chin, and below it is the platform overlay. Put HEAD captions ABOVE the head (y≈350–470, under the top tags), keep DARK captions low. Compute it from the face track, don't guess (`Elastic-search-interview`).
- When I sit further back (face ~400 px, chin ≈ y 880, `bloom-filter`), the brand's lower third (y≈1250) is clear of the face again. Decide per video from the face track.
- Keep a sentence/clause-end mark on each caption word (`p` from the script token's `.?!:,`) and break pages on it. Stripping punctuation for display before the page-break check let 1–2-word pages straddle sentences ("ship | RAG", "LLM | So") on `rag-pipeline`; it showed up at trailer joins first.
