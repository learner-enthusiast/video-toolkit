# Trailer

**Goal:** two trailers for every video, cut from the same approved timeline: one landscape, one portrait.

**Cut**
- Length 30–60 s (15–20 s when the main video is itself a reel). One idea: the problem, the payoff, and a reason to watch the full video.
- Open on the boldest line or result, never a greeting. A 2–5 word text hook is on screen from frame 0.
- Reuse beats, graphics and word timestamps from the main edit. Don't re-pick takes.
- End on a short `EndCard` (≤ 2 s) that points to the full video.

**Two formats**
- **Landscape** (1920x1080, 30 fps): the main video's framing and caption style.
- **Portrait** (1080x1920, 30 fps): follow the `/reel` rules for framing, big captions and safe zones. If the source is landscape, use `components/FaceTrackedCrop.md` for talking-head beats and stack me on top of the screen for screen beats. Never stretch.
- Build both as separate Remotion compositions sharing one beat list, so a change to the cut updates both.

**Deliver**
- Render and encode per `render.md`: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`, each with an SRT (`subtitles.md`).
- Both go through `qa.md` like the main video.
