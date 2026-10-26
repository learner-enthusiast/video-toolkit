# TypingIntro

**Purpose:** a cold open (about 4 s): a line of code-style text types out on black before my first word.

**Props:** `text` (e.g. `> building things that ship_`), `cps`, `blinks`.

**Look**
- A near-black background. JetBrains Mono 500 at about 56 px, centered vertically and left-aligned to a centered block.
- The prompt character `>` in the accent color and the rest in text color. Use a block cursor.

**Motion**
- Characters type at about 14–18 per second with slight human jitter (seeded, so it is deterministic per render).
- A key-click SFX per character at low volume, and a slightly louder click on spaces.
- After typing, the cursor blinks twice (about 15 frames on, 15 off), then everything fades into the first TALK shot.

**Gotchas**
- No captions over it. Its duration adds to the timeline before the first spoken word.
- Use seeded randomness only (Remotion `random(seed)`), never `Math.random()`.
