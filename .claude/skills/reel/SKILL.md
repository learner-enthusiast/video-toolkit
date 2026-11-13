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
- **Layout.** There is no default layout. Every beat is HEAD (my face fills the frame), FULL (graphic fills the frame, my face hidden, voice continues) or SPLIT (graphic on top, me docked below), per `brand.md` Layout and `components/layout-states.md`. Read the script's `[mm:ss–mm:ss | HEAD|FULL|SPLIT]` tags as the plan, mix all three, and switch by hard cut or brand wipe only where a concept starts or ends. HEAD uses the portrait recording natively. Keep the face out of the top ~12% and bottom ~20% UI zones.
- **Creative direction.** Script cues are the baseline, not a limit: bring a better visual take where it explains better, within the rules in `CLAUDE.md` (never change spoken lines, facts or code, `brand.md`, the length limit, or a cue's intent). List a "Creative take" in the storyboard; small changes just do and log, bigger ones go to 3 approval stills for my OK.
- **Playlists.** If the project sits in a playlist (`projects/<playlist>/<NN>-<topic>/`), also follow `series/<playlist>.md`.
- **Big captions.** See `components/Captions.md` (reel mode): 1–3 words at a time, ~80 px, placed per state (HEAD lower third clear of the face, SPLIT in the strip, FULL in a band clear of the graphic's key element).
- **Safe zones.** Keep text clear of the right ~15% (platform buttons) and the bottom ~20% (description overlay).
- **Ending.** End on a payoff line or a loop back to the hook. A short `EndCard` (≤ 2 s) is optional.
- **Deliver.** `out/<name>_9x16.mp4` plus an SRT, at -14 to -16 LUFS. Always make a thumbnail with `pipeline/thumbnail.md` (9:16 variant).
- **Trailer.** Always make exactly one short cut, rendered in both aspect ratios: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4` (`pipeline/trailer.md`). If the prompt defines a short cut, that is the trailer; otherwise the default 15–20 s trailer. Never both.
- **Carousel twin.** After the final render's QA, run `/carousel <name>` (`pipeline/carousel.md`): 6–8 slides in `out/carousel/`, with its outline and slide-1 approval stops.
- **Social copy.** Always write `out/<name>_social.json` per `pipeline/social-copy.md`. YouTube chapters don't apply to a reel; use the `shorts_title` and a short description instead.

Stop at the rough cut for my OK, as always.
