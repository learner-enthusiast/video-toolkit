# FaceAvatar

**Purpose:** a character in a story-led short, shown only as a circle-cropped face still that I supply (never a fetched show still, clip or logo). Reusable for any character-led explainer.

**Props:** `mood` (which supplied still: e.g. worried | happy), `size`, `focus` (0–1, orange ring), `at`, `out`, `shakeAt`, `bounceAt`, `tiltAt`, `dim`.

**Look**
- Circle crop centred on the face (hair to chin inside the circle), 2 px near-black border, white behind.
- In focus: a 6 px orange ring 10 px outside the border. Out of focus: no ring; `dim` desaturates it for background use (end card).
- Sizes: ~110 px as a speaker badge, ~200–250 px as the subject of a card.

**States**
- idle: still.
- shake (wrong): horizontal sine, 12 px, decays over 18 frames.
- bounce (relieved/thrilled): one 26 px hop over 14 frames; swap to the happy still on the same frame.
- worried tilt: rotate to −9° on a soft spring.

**Gotchas**
- Store the crop per still (face centre + square side in source px); never `object-fit` a whole poster into the circle.
- If the supplied stills have different art styles, never show two moods side by side; swap in place.
- If the file is missing, ask me. Do not source one.
- All timings trigger on spoken-word frames; every instance has an exit.
