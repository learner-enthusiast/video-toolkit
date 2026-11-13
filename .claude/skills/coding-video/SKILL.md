---
name: coding-video
description: 16:9 coding video pipeline (tutorial or project demo) from raw talking-head and screen footage to a delivered MP4 with SRT.
argument-hint: <name>
---

# Coding video (16:9, 1920x1080, 30 fps)

Work in `projects/<name>/` (or `projects/<playlist>/<NN>-<topic>/` for a playlist episode; then also follow `series/<playlist>.md`). Read `CLAUDE.md` and `brand.md` first. Follow each step's file in `pipeline/`.

Run this as four stages, one session each (`pipeline/stages.md`). Start each stage by reading `log.md` and the project files, and end it with a handoff in `log.md`. Shell work goes to Haiku as exact-command batches (`pipeline/delegation.md`). Vision goes through contact sheets (`pipeline/video-inspect.md`).

**Stage 1 · Prep** (steps 1–4)

1. **GPU:** `pipeline/gpu.md`. Do not continue until the checks pass.
2. **Probe and trim:** `pipeline/probe-and-trim.md`. Report every file's resolution, rotation, fps and duration.
3. **Clean audio:** `pipeline/clean-audio.md`.
4. **Transcribe:** `pipeline/transcribe.md`.
**Stage 2 · Cut** (steps 5–6)

5. **Take selection:** `pipeline/take-selection.md`, using `/cut-video` as the cutting engine (MFA word boundaries, ground-truthed windows, trim+concat render) with `balanced` tone. The pause lengths and the keep-last-take rule in `take-selection.md` win. Write `work/cutlist.md`.
6. **CHECKPOINT:** render a 720p rough cut (talking head + clean audio) to `out/roughcut_preview.mp4`. Show me the cutlist summary and any weak or missing lines. **Wait for my OK.** Write the handoff and end the session here.

**Stage 3 · Compose** (steps 7–8; only after my OK is recorded in `log.md`)

7. **Composition:** `pipeline/composition.md`. Lay every beat out as HEAD, FULL or SPLIT (`brand.md` Layout, `components/layout-states.md`; no default, mix all three, read the script's `[mm:ss–mm:ss | STATE]` tags as the plan). For HEAD framing: crop if the source is ≥ 1440 px wide, otherwise `components/PresenterSplit.md`. Tell me which and why. Be a creative co-director: cues are the baseline, bring a better take within the rules in `CLAUDE.md` (Creative direction); write a "Creative take" list in `work/storyboard.md`, do small improvements and log them, and show bigger changes in 3 approval stills for my OK. Use `/add-zooms` to write the punch/ratchet map from the word timestamps. It decides where the ~108% framing lands to hide each jump cut, and those zooms are applied in the composition. No Ken Burns from add-zooms: do slow pushes in Remotion with ease-in-out.
8. **Render:** `pipeline/render.md`.
**Stage 4 · Deliver** (steps 9–14)

9. **Subtitles:** `pipeline/subtitles.md`.
10. **Trailers:** `pipeline/trailer.md`. Always make both: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`.
11. **QA:** `pipeline/qa.md`, on the main video and both trailers. Look at every contact sheet yourself before delivering. Fix what fails before reporting.
12. **Thumbnail:** `pipeline/thumbnail.md`. Always.
13. **Social copy:** `pipeline/social-copy.md`. Always write `out/<name>_social.json`.
14. **Report:** list every file in `out/`, plus durations, loudness, choices made, lines worth re-recording, and anything you couldn't do. Then fold any lessons back into the toolkit `.md` files.
