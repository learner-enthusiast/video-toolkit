# FaceTrackedCrop

**Purpose:** a crop window that follows my head like a slow camera operator. It feeds `PresenterSplit`, `Bubble` and 9:16 framing.

**Data:** `public/data/face.json`, with per-frame face center and size in source pixels, made by a Python script in `work/`.

**Build the track**
- Run MediaPipe face detection (BlazeFace short-range, Tasks API; `mp.solutions` no longer exists) on every frame of the CFR source.
- Fill gaps by interpolation and report the detection rate.
- Smooth heavily: a median filter to kill spikes, then a slow critically damped smoother (seconds, not frames). Add a dead zone, so small head moves don't move the camera.

**Component props:** `track`, `aspect` (1, 9:16 or the card's), `zoom`, `headroom`.

**Behaviour**
- Compute a crop rect from the smoothed center and zoom, clamped to the source bounds (never show beyond the frame edges).
- Render it with `OffthreadVideo` positioned inside an `overflow: hidden` box, never by stretching.

**Gotchas**
- The track must be in the same coordinates as the upright CFR working copy, not the rotated original.
- Keep the head at about a third from the top, never centered vertically.
