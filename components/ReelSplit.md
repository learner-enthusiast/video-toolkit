# ReelSplit (the SPLIT state)

**Purpose:** the SPLIT state of the three-state layout (`components/layout-states.md`, `brand.md` Layout): grid card on top, caption strip, me docked at the bottom. It is one option chosen per beat, not the default. Use it when my reaction or delivery matters while a simple graphic is on screen; dense code or detailed diagrams go FULL.

**Props:** `face` track, `segments` (picture cuts), `states` (HEAD | FULL | SPLIT, each with `from`/`to` frames; DARK is a style flag on any of them), `punch` per segment.

**Geometry (1080x1920)**
- HEAD (neighbouring state): me full frame. Portrait source natively; a landscape source face-track-cropped to 9:16 (`FaceTrackedCrop`).
- SPLIT (this state): grid card at the top inside the 5% margin (~970–980 px tall: 1920 − 96 top margin − ~120 caption strip − 581 strip − ~134 lift; "~1190" does not fit), caption strip below it, then me as a 16:9 window 1080x608 (radius and 2 px border from `brand.md`), lifted ~120 px off the bottom so the platform caption overlay never covers my face.
- A portrait source in SPLIT shows a face-tracked 16:9 head-and-shoulders crop; a landscape source is scaled to 1080 wide.
- DARK: the dark style fills the frame (punch moments); me dimmed in HEAD, or in the docked window.

**Motion**
- HEAD ↔ SPLIT and FULL ↔ SPLIT: one ~0.4 s spring on the video rect (x, y, w, h, radius) and the crop window together, while the grid card slides down from the top. A hard cut into or out of SPLIT is also allowed on a beat boundary (`layout-states.md`); never linear.
- Punch-ins alternate 100% / ~108% on picture cuts to hide jump cuts, in every state.

**Gotchas**
- Portrait source in SPLIT: a 16:9 crop is too tight (forehead and chin cut). Use the square head-and-shoulders crop with blurred sides, and morph INTO it: interpolate the inner rect and the crop aspect (9:16 → 1:1) and fade the blur in. Switching crop style when the morph ends is a visible snap.
- Hide captions for the first ~9 frames of a morph into or out of SPLIT and fade them back in. Otherwise the caption band crosses the moving video and passes over my face.
- Compute every rect in one geometry module; components get rects, never invent positions.
- Captions sit in the strip in SPLIT and in the lower third in HEAD; they move with the morph.
- Graphics inside the grid card are positioned in CARD-LOCAL coordinates (the card is the positioning context). Using frame coordinates shifts everything by the card's x/y and overflows the right edge.
- Close-up portrait source: in the square SPLIT crop use the full source width (1080 px) with the face at ~60% of the crop height, or the hair is cut.
- Scale the square crop with the face: face ~620 px → 1080 px crop; face ~400 px → ~960 px crop with the face at ~40%. A 760 px crop on a 400 px face shows only head and mic (`bloom-filter`).
- FULL state (graphic full frame, my audio only; `layout-states.md`): the grid card grows to ~972x1400 inside the margin, my docked strip slides off the bottom with the same spring, and captions drop to a band just below the card. Draw scenes in one fixed 972x971 space centred in the card so a scene can morph SPLIT ↔ FULL; a scene that only lives in FULL may use the extra ±214 px. A sparse scene in FULL looks empty: scale it up from the card's top-left (×1.35) and let it shrink back when the layout returns to SPLIT (`rate-limiter` AnswerGrid).
- Face ~460 px wide in the portrait source: the square SPLIT crop needs the full 1080 px width with the face at ~42% of the crop; 960 px cut the hair (`rate-limiter`).
- Face ~387 px wide in a 1080×1920 phone source, sitting back with a mic boom on one side: square SPLIT crop 960 px with the face at 40% worked; HEAD crop centred 85% toward the face x (`rag-pipeline`).
- Corner pills inside the card (an "INTERVIEW QUESTION" tag top-right) collide with scene tags placed at the same spot: on `jwt-explained` the orange pill fully hid the "Base64URL" tag. Reserve the card's top-right 420×80 for the corner pill whenever one is shown, and check the beat's stills for hidden tags.
- Portrait source + a large third-party image above my head (e.g. a creator's thumbnail I'm summarising): scale the whole plate to ~0.78, bottom-anchored, with the brand border/radius (`docker-is-dead` HOOK pose, `GEO.hookPanel` 842x1498 at y 422). Uniform scale, never a stretch; it frees y ≈ 214–690 for graphics and morphs into SPLIT with the same spring. My head top moved from y ≈ 820 (hook) to ≈ 755 (verdict) over one recording: measure it in a still of every HEAD scene and keep graphics above it.
