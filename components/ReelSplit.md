# ReelSplit

**Purpose:** the 9:16 layout system: FULL (me only) and SPLIT (grid card on top, caption strip, me docked at the bottom), with a smooth morph between them.

**Props:** `face` track, `segments` (picture cuts), `modes` (FULL | SPLIT | DARK, each with `from`/`to` frames), `punch` per segment.

**Geometry (1080x1920)**
- FULL: me full frame. Portrait source natively; a landscape source face-track-cropped to 9:16 (`FaceTrackedCrop`).
- SPLIT: grid card at the top inside the 5% margin (~970–980 px tall: 1920 − 96 top margin − ~120 caption strip − 581 strip − ~134 lift; "~1190" does not fit), caption strip below it, then me as a 16:9 window 1080x608 (radius and 2 px border from `brand.md`), lifted ~120 px off the bottom so the platform caption overlay never covers my face.
- A portrait source in SPLIT shows a face-tracked 16:9 head-and-shoulders crop; a landscape source is scaled to 1080 wide.
- DARK: the dark style fills the frame (punch moments); me hidden or in the docked window.

**Motion**
- FULL ↔ SPLIT: one ~0.4 s spring on the video rect (x, y, w, h, radius) and the crop window together, while the grid card slides down from the top. Never a hard cut.
- Punch-ins alternate 100% / ~108% on picture cuts to hide jump cuts, in both modes.

**Gotchas**
- Portrait source in SPLIT: a 16:9 crop is too tight (forehead and chin cut). Use the square head-and-shoulders crop with blurred sides, and morph INTO it: interpolate the inner rect and the crop aspect (9:16 → 1:1) and fade the blur in. Switching crop style when the morph ends is a visible snap.
- Hide captions for the first ~9 frames of a FULL ↔ SPLIT morph and fade them back in. Otherwise the caption band crosses the moving video and passes over my face.
- Compute every rect in one geometry module; components get rects, never invent positions.
- Captions sit in the strip in SPLIT and in the lower third in FULL; they move with the morph.
- Graphics inside the grid card are positioned in CARD-LOCAL coordinates (the card is the positioning context). Using frame coordinates shifts everything by the card's x/y and overflows the right edge.
- Close-up portrait source: in the square SPLIT crop use the full source width (1080 px) with the face at ~60% of the crop height, or the hair is cut.
- Scale the square crop with the face: face ~620 px → 1080 px crop; face ~400 px → ~960 px crop with the face at ~40%. A 760 px crop on a 400 px face shows only head and mic (`bloom-filter`).
