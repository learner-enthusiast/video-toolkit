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
