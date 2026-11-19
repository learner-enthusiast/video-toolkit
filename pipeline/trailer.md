# Trailer

**Goal:** exactly one short-form cut per video, rendered twice from the same approved timeline: one landscape (16:9), one portrait (9:16). Never two different short cuts.

**Cut**
- **Which cut:** if the prompt defines a short cut (e.g. a "60-second cut" with a beat list), that cut IS the trailer: use the prompt's length and beats. Otherwise use the default trailer below. Never ship both a prompt-defined cut and a default trailer.
- Default trailer: length 30–60 s (15–20 s when the main video is itself a reel). One idea: the problem, the payoff, and a reason to watch the full video.
- Open with "Namoshkar!" (~1.5 s with the pause), then the boldest line or result as the hook. A 2–5 word text hook is on screen from frame 0. Reuse the main edit's "Namoshkar!" take.
- Reuse beats, graphics and word timestamps from the main edit. Don't re-pick takes.
- End on a one-line recap, then "Bye bye, sayonara!" with a wave (reused from the main edit), then a short `EndCard` (≤ 2 s) that points to the full video.

**Two formats**
- **Landscape** (1920x1080, 30 fps): the main video's framing and caption style.
- **Portrait** (1080x1920, 30 fps): follow the `/reel` rules for framing, big captions and safe zones. If the source is landscape, use `components/specs/FaceTrackedCrop.md` for talking-head beats and stack me on top of the screen for screen beats. Never stretch.
- Build both as separate Remotion compositions sharing one beat list, so a change to the cut updates both.
- Simplest build: replay the main composition per segment, `<Sequence from={offset} durationInFrames={b - a}><Sequence from={-a}><Main trailer /></Sequence></Sequence>`. Voice, SFX, captions and scenes stay in sync; hide anything that would jump between segments (a running countdown) with a `trailer` prop (`graphql-vs-rest`).

**Deliver**
- Render and encode per `render.md`: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`, each with an SRT (`subtitles.md`).
- Both go through `qa.md` like the main video.
- End a replayed segment 2 frames after its last word when the main's next line starts right after it: the default 8-frame tail caught the next scene's fade and the first caption word (`rag-pipeline`). Start a segment exactly on its first word for the same reason.
- Replaying Main per segment opens each segment on the last frames of the PREVIOUS main scene's fade-out when that scene isn't in the trailer (`vectorless-rag`: the R1 segment began with a ghost of T2's "WON'T FIT" for ~6 frames). Give scenes a trailer flag (a React context set by `Main`'s `trailer` prop) that cuts them 3 frames before their `out` instead of cross-fading, and end a segment at `min(last word + 4, next scene start − 10)` so it never runs into that cut (an empty card showed for the last frames of K2).
- A dark trailer `EndCard` that fades in from black reads as a black flash after a bright HEAD beat (video-inspect `black_flash` 0.13 s). Cut it in; fade only its exit.
