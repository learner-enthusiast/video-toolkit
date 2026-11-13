# Layout states (HEAD / FULL / SPLIT)

**Purpose:** the three-state layout system. Every beat is in exactly one state. There is no default; pick per beat from what the viewer must understand. `brand.md` (Layout) is the rule, this file is the build spec. Applies to 9:16 and 16:9.

**Props:** `face` track, `segments` (picture cuts), `states` (HEAD | FULL | SPLIT, each with `from`/`to` frames, from the script's `[mm:ss–mm:ss | STATE]` cues), `transition` per switch (`cut` | `wipe`), `dark` flag for punch moments.

**The states**
- **HEAD:** my face fills the frame; captions and lower-thirds on top. For story beats, emotion, reactions, transitions, punchlines.
- **FULL:** the graphic fills the whole frame, my face is hidden, my voice continues. For flows, code, timelines, comparisons, data, anything dense. 9:16 card: ~972x1400 inside the margin; draw scenes in the fixed 972x971 space centred in it so a scene can also live in SPLIT, and scale a sparse scene up (×1.35 from the card's top-left) so it doesn't look empty.
- **SPLIT:** graphic on top, my face below (`components/ReelSplit.md`). For a simple graphic (one card, a short list, a number, a punchline pointing at a visual) while my delivery matters. Never dense code or detailed diagrams: those go FULL.
- Mix all three. A video that stays in one state for most of its length is wrong; HEAD is for the story, FULL for the concept, SPLIT for the reaction on a simple visual.

**Transitions**
- **Cut:** a hard cut, only on a beat boundary or on an emphasised word. Pair it with a 100% ↔ ~108% punch change so it also hides a jump cut.
- **Wipe:** a brand-style fluid wipe: the incoming state slides or scales in on one ~0.4 s spring (or ease-in-out) over the outgoing one; orange edge optional. Never linear, never a cross-dissolve.
- HEAD ↔ SPLIT and FULL ↔ SPLIT can morph shared rects (video rect, card) with the SPLIT spring; HEAD ↔ FULL is a cut or wipe.
- Switch only where a concept starts or ends. Never mid-sentence unless the cut lands on an emphasised word.

**Caption placement** (captions stay on in every state; never over a graphic's key element)
- HEAD, 9:16: lower third on an off-white block, clear of the chin and of the bottom ~20% platform overlay. Compute from the face track (see `components/Captions.md`).
- HEAD, 16:9: bottom centre inside the safe margin, ≤ 2 lines.
- SPLIT, 9:16: the off-white strip between the card and the docked head.
- FULL, 9:16: a band just below the card (or above the platform overlay), clear of the graphic's key element. 16:9: bottom centre, over a part of the card with no content, or on an off-white block.
- Hide captions for the first ~9 frames of a morph and fade them back in.

**Framing the talking head**
- Portrait phone footage (1080x1920): face centred, safe margins for 9:16 UI: face out of the top ~12% and bottom ~20%, nothing important in the right ~15%.
- HEAD, 9:16: the portrait source natively. A landscape source is face-tracked and centre-cropped to portrait (`FaceTrackedCrop`).
- HEAD, 16:9: crop if the source is ≥ 1440 px wide, otherwise `PresenterSplit`.
- SPLIT, 9:16: a landscape source is a 16:9 window scaled to 1080 wide; a portrait source gets a face-tracked head-and-shoulders square (face ~40–60% down the crop) on a blurred, darkened copy filling the sides. A 16:9 crop of a portrait frame cuts forehead and chin.
- Never stretch me; never cover my face with a graphic or caption.

**Gotchas**
- Compute every rect for the three states in one geometry module; components get rects, never invent positions.
- A graphic that lives in both FULL and SPLIT is drawn once in card-local coordinates and scaled, never redrawn.
- Hiding my face in FULL does not change the audio: the voice WAV keeps playing on the output timeline.
