---
code: components/code/brand2/CamFrame/CamFrame.tsx
preview: components/code/brand2/CamFrame/preview.png
props: "cam, startTime, kicker, at, out"
variants: "with/without kicker"
last_used: "—"
---
# CamFrame

**Purpose:** a CCTV viewfinder over a beat about watching, logging or privacy.

**Props:** `cam`, `startTime` ("dd-mm-yyyy hh:mm:ss"), `kicker`, `at`, `out`.

**Look**
- Four corner brackets; a red dot and "REC" top-left; "CAM 0N" top-right; the timestamp bottom-left; an optional accent mono kicker under REC.
- Fills its parent. The dot is the one use of the `alert` colour outside a failure stamp.

**Motion**
- Fades in over 8 frames; the dot pulses once a second; the timestamp counts with the frame.
- Exit: fade over 8 frames.

**Gotchas**
- Over my face, keep the brackets and labels outside it.
- The time is illustrative: never present it as a real recording.

## Code

Saved: `components/code/brand2/CamFrame/CamFrame.tsx` (preview: `preview.png`, rendered in Brand 2). A Brand 2 signature piece: import `shared/brand2/CamFrame/CamFrame`. If another brand needs it, move its folder up to the shared library, next to the other shared components; never copy. Brand values come from `components/code/theme.ts`.

- Code props: cam, startTime, kicker, at, out.
- New for the three-brand setup; not yet used in a finished video.
