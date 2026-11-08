# Trailer

**Goal:** exactly one short-form cut per video, rendered twice from the same approved timeline: one landscape (16:9), one portrait (9:16). Never two different short cuts.

**Cut**
- **Which cut:** if the prompt defines a short cut (e.g. a "60-second cut" with a beat list), that cut IS the trailer: use the prompt's length and beats. Otherwise use the default trailer below. Never ship both a prompt-defined cut and a default trailer.
- Default trailer: length 30–60 s (15–20 s when the main video is itself a reel). One idea: the problem, the payoff, and a reason to watch the full video.
- Open on the boldest line or result, never a greeting. A 2–5 word text hook is on screen from frame 0.
- Reuse beats, graphics and word timestamps from the main edit. Don't re-pick takes.
- End on a short `EndCard` (≤ 2 s) that points to the full video.

**Two formats**
- **Landscape** (1920x1080, 30 fps): the main video's framing and caption style.
- **Portrait** (1080x1920, 30 fps): follow the `/reel` rules for framing, big captions and safe zones. If the source is landscape, use `components/FaceTrackedCrop.md` for talking-head beats and stack me on top of the screen for screen beats. Never stretch.
- Build both as separate Remotion compositions sharing one beat list, so a change to the cut updates both.
- Simplest build: replay the main composition per segment, `<Sequence from={offset} durationInFrames={b - a}><Sequence from={-a}><Main trailer /></Sequence></Sequence>`. Voice, SFX, captions and scenes stay in sync; hide anything that would jump between segments (a running countdown) with a `trailer` prop (`graphql-vs-rest`).

**Deliver**
- Render and encode per `render.md`: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`, each with an SRT (`subtitles.md`).
- Both go through `qa.md` like the main video.
- End a replayed segment 2 frames after its last word when the main's next line starts right after it: the default 8-frame tail caught the next scene's fade and the first caption word (`rag-pipeline`). Start a segment exactly on its first word for the same reason.
