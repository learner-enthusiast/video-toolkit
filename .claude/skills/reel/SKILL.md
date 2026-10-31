---
name: reel
description: 9:16 reel pipeline (1080x1920, 30–60 s) with a hook in the first 2 s, big captions and fast pace.
argument-hint: <name>
---

# Reel (9:16, 1080x1920, 30 fps, 30–60 s)

Use the same pipeline steps and the same four stages as `/coding-video` (GPU, probe, clean audio, transcribe, take selection, rough cut checkpoint, composition, render, QA), with the same delegation and vision rules (`pipeline/stages.md`, `pipeline/delegation.md`, `pipeline/video-inspect.md`). These rules change:

- **Skills.** Cut with `/cut-video` (`aggressive` tone, but this file's pause lengths win), and punch in with `/add-zooms` (punches and ratchets only). If the source is a long video, use `/clipify` (dialogue mode) to pick 3–5 candidate moments. Show them to me, then build each chosen one as a reel with the rules below.

- **Hook in the first 2 s.** Open on the boldest claim or result, never a greeting. A big text hook (2–5 words) is on screen from frame 0. If the strongest line is mid-recording, move it to the front.
- **Length 30–60 s.** Cut to one idea. Tighten pauses harder: about 0.10 s between phrases and 0.15 s between sentences.
- **Fast pace.** The visual changes every 1.5–3 s (punch-in, a screen, a graphic, a card). No beat holds still.
- **Framing.** Use the portrait recording natively, full frame. In screen beats, me in the top half and the screen or graphic in the bottom half. Keep the face out of the top ~12% and bottom ~20% UI zones.
- **Big captions.** See `components/Captions.md` (reel mode): 1–3 words at a time, ~80 px, centered at mid-frame between my face and the screen.
- **Safe zones.** Keep text clear of the right ~15% (platform buttons) and the bottom ~20% (description overlay).
- **Ending.** End on a payoff line or a loop back to the hook. A short `EndCard` (≤ 2 s) is optional.
- **Deliver.** `out/<name>_9x16.mp4` plus an SRT, at -14 to -16 LUFS. Always make a thumbnail with `pipeline/thumbnail.md` (9:16 variant).
- **Trailers.** Always make both 15–20 s trailers per `pipeline/trailer.md`: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`.
- **Social copy.** Always write `out/<name>_social.json` per `pipeline/social-copy.md`. YouTube chapters don't apply to a reel; use the `shorts_title` and a short description instead.

Stop at the rough cut for my OK, as always.
