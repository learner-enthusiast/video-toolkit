# Bubble

**Purpose:** me as a rounded picture-in-picture during SCREEN and GFX beats.

**Props:** `face` track, `rect` (from layout), `at`/`out` frames, `corner` (default bottom-right).

**Look**
- About 22% of frame width, square, with radius 16, the brand shadow and a 2 px accent border.
- Contents: a square crop centered on my smoothed face track (see `FaceTrackedCrop.md`), with the head at about 40% from the top.
- Sits inside the 5% safe margin.

**Motion**
- Morph from the presenter card (or full frame) into the bubble with one spring on x, y, w, h and radius together. Never cut between them.
- On exit, morph back the same way.

**Gotchas**
- Captions must move up whenever the bubble occupies the bottom band (see `Captions.md`).
- The URL pill and highlights must avoid the bubble rect, so pass it to them.
- Use the same graded source as TALK mode, so skin tone doesn't jump.
