# EndCard

**Purpose:** a 5 s close after my last word, with my links from `brand.md`.

**Props:** `links`, `bg` (a frame or clip to use as background), `dur`.

**Look**
- Background: the last frame of a project clip (e.g. the website), heavily blurred and darkened to about 30% brightness.
- A centered stack of the links in Inter 600 at about 40 px, with the primary site larger, plus a small line icon per link (globe, LinkedIn, GitHub, mail).
- Optional small "Thanks for watching" kicker in dim text above.

**Motion**
- Links fade and rise in, staggered by 5 frames.
- Hold, then the whole frame fades to black over the last 15 frames, with audio fading at the same time.

**Gotchas**
- Leave no captions. No music spike: the music slot ducks out with the fade.
- In 9:16, keep the stack in the center third (platform UI covers the bottom).
- Tight length budget (e.g. a hard 2:59 cap): show the card as a white panel over my chest while I say the last lines (captions off), then fade to black ~1 s after the last word, instead of a full-screen card after it (`bloom-filter`).
