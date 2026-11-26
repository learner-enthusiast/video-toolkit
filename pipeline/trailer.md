# Trailer

**Goal:** exactly one short-form cut per video. Never two different short cuts.
- **Reel (main video ≤ 2:59):** rendered once, portrait 9:16 (1080x1920). No landscape version.
- **Long-form (main video > 3:00):** rendered twice from the same approved timeline: one landscape (16:9), one portrait (9:16).

**Cut**
- **Which cut:** if the prompt defines a short cut (e.g. a "60-second cut" with a beat list), that cut IS the trailer: use the prompt's length and beats. Otherwise use the default trailer below. Never ship both a prompt-defined cut and a default trailer.
- Default trailer: length 30–60 s (15–20 s when the main video is itself a reel). One idea: the problem, the payoff, and a reason to watch the full video.
- Opener per `CLAUDE.md` → House numbers (hook first), with the boldest line or result as the hook and a 2–5 word text hook. Reuse the main edit's "Namoshkar!" take.
- Reuse beats, graphics and word timestamps from the main edit. Don't re-pick takes.
- Close per `CLAUDE.md` → House numbers (reused from the main edit), then a short `EndCard` (≤ 2 s) that points to the full video.

**Formats**
- **Portrait** (1080x1920, 30 fps; every video): follow the `/reel` rules for framing, big captions and safe zones. If the source is landscape, use `components/specs/FaceTrackedCrop.md` for talking-head beats and stack me on top of the screen for screen beats. Never stretch.
- **Landscape** (1920x1080, 30 fps; long-form only): the main video's framing and caption style.
- Long-form: build both as separate Remotion compositions sharing one beat list, so a change to the cut updates both. Reel: one portrait trailer composition.

**Deliver**
- Render and encode per `render.md`, each with an SRT (`subtitles.md`). Reel: `out/<name>_trailer_9x16.mp4` only. Long-form: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`.
- Every trailer render goes through `qa.md` like the main video.

**Gotchas**
- Replay Main per segment with nested `Sequence`s; hide anything that jumps between segments with a `trailer` prop.
- End a replayed segment 2 frames after its last word if the next line follows at once; start it exactly on its first word.
- Trailer flag cuts scenes 3 frames before `out`; end a segment at `min(last word + 4, next scene start − 10)` to avoid ghost frames.
- Cut in a dark trailer `EndCard` (a fade-in reads as a black flash); fade only its exit.
