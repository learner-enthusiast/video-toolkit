# PresenterSplit

**Purpose:** 16:9 TALK layout when the portrait source is under 1440 px wide (a crop would look soft).

**Props:** `face` track, `segments` (picture cuts), `side` (default left), `punch` per segment.

**Look**
- Me in a tall rounded portrait card at about 38% width and full height minus the 5% margins, with the brand radius, shadow and border.
- The other side is free for the beat's graphics on the same grid.
- Background: a heavily blurred (about 60 px), darkened (about 35% brightness) copy of my video, scaled to cover, plus a soft vignette. It must read as a broadcast layout, not black bars.

**Motion**
- Punch-in: alternate 100% / ~108% scale on every picture cut to hide jump cuts, anchored on the face, never cropping the chin or forehead.
- A slow 1–2% drift inside a long segment keeps it alive.
- The card morphs into `Bubble` for SCREEN/GFX beats and back.

**Gotchas**
- Blur the backdrop from a downscaled copy. Blurring at full resolution makes renders crawl.
- Never stretch the portrait source to fill the card. Crop it.
- Tell me in the report that this mode was used and why.
