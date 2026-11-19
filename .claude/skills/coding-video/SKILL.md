---
name: coding-video
description: 16:9 coding video pipeline (tutorial or project demo) from raw talking-head and screen footage to a delivered MP4 with SRT.
argument-hint: <name>
---

# Coding video (16:9, 1920x1080, 30 fps)

Work in `projects/<name>/` (or `projects/<playlist>/<NN>-<topic>/` for a playlist episode; then also follow `series/<playlist>.md`). Read `CLAUDE.md` and `brand.md` first. Logos come from `icons/` (`icons/icons.md`; download an official one into `icons/` only if missing). Choose components from `components/index.md` first; open only the specs you will use. Follow each step's file in `pipeline/`.

Run this as four stages, one session each (`pipeline/stages.md`). Start each stage by reading `log.md` and the project files, and end it with a handoff in `log.md`. Shell work goes to Haiku as exact-command batches (`pipeline/delegation.md`). Vision goes through contact sheets (`pipeline/video-inspect.md`).

**Stage 1 · Prep** (steps 1–9; execute in this order)

1. **Inspect and probe original footage:** read `pipeline/probe-and-trim.md`; probe every original source and report resolution, rotation, fps, duration, and audio streams. Never modify `raw/` or `assets/`.
2. **Identify recordings:** inventory every relevant talking-head recording/audio stream and assign each a unique stable ID.
3. **Read the gate:** read `pipeline/voice-cleaning.md` before any Whisper call.
4. **Clean every recording:** for each source, run `vt-python tools/clean_audio.py "projects/<name>/raw/<recording>" "projects/<name>/work/audio/cleaned/<recording-id>.wav" --preset studio --mode quality --report "projects/<name>/work/audio/reports/<recording-id>-clean-report.json"`. Keep each source, output and report distinct; never overwrite raw footage or an earlier result.
5. **Inspect each report:** check source/output identity, duration delta, before/after LUFS and true peak, and clipping indication.
6. **Confirm both model stages per report:** require `dereverberation.applied: true` and `speech_enhancement.status: processed` with model `DeepFilterNet3`. On any failure, stop Prep and report it; no substitute mode or original-audio ASR without my explicit approval.
7. **Listen to every original/cleaned pair:** check echo, hiss, clarity, natural voice identity, clipping/distortion/artifacts and sync. If listening is unavailable, disclose this and request my approval before transcription.
8. **Transcribe only after all recordings pass steps 5–7:** perform the GPU preflight in `pipeline/gpu.md` if needed, then follow `pipeline/transcribe.md` using each verified cleaned WAV. Do not transcribe a raw source, proxy audio extraction, or unverified cleaned file.
9. **Continue remaining Prep:** finish transcript checks and other Prep artifacts, then record the per-recording source → clean WAV → report mapping and gate results in the handoff. `/coding-video` may not proceed to cut selection with an unverified voice recording.

**Stage 2 · Cut** (steps 10–11)

10. **Take selection:** `pipeline/take-selection.md`, using `/cut-video` as the cutting engine (MFA word boundaries, ground-truthed windows, trim+concat render) with `balanced` tone. The pause lengths and the keep-last-take rule in `take-selection.md` win. Write `work/cutlist.md`.
11. **CHECKPOINT:** render a 720p rough cut (talking head + verified clean audio) to `out/roughcut_preview.mp4`. Show me the cutlist summary and any weak or missing lines. **Wait for my OK.** Write the handoff and end the session here.

**Stage 3 · Compose** (steps 12–13; only after my OK is recorded in `log.md`)

12. **Composition:** `pipeline/composition.md`. Lay every beat out as HEAD, FULL or SPLIT (`brand.md` Layout, `components/specs/layout-states.md`; no default, mix all three, read the script's `[mm:ss–mm:ss | STATE]` tags as the plan). For HEAD framing: crop if the source is ≥ 1440 px wide, otherwise `components/specs/PresenterSplit.md`. Tell me which and why. Be a creative co-director: cues are the baseline, bring a better take within the rules in `CLAUDE.md` (Creative direction); write a "Creative take" list in `work/storyboard.md`, do small improvements and log them, and show bigger changes in 3 approval stills for my OK. Use `/add-zooms` to write the punch/ratchet map from the word timestamps. It decides where the ~108% framing lands to hide each jump cut, and those zooms are applied in the composition. No Ken Burns from add-zooms: do slow pushes in Remotion with ease-in-out.
13. **Render:** `pipeline/render.md`.

**Stage 4 · Deliver** (steps 14–20)

14. **Subtitles:** `pipeline/subtitles.md`.
15. **Trailers:** `pipeline/trailer.md`. Always make both: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`.
16. **QA:** `pipeline/qa.md`, on the main video and both trailers. Look at every contact sheet yourself before delivering. Fix what fails before reporting.
17. **Thumbnail:** `pipeline/thumbnail.md`. Always.
18. **Social copy:** `pipeline/social-copy.md`. Always write `out/<name>_social.json`.
19. **Save components:** `CLAUDE.md` (Components, Deliver): clean up every new or extended component that worked, save it to `components/code/` with a `preview.png`, update its spec and `components/index.md`, set `last_used` on every component the video used. Logos: confirm every icon used is in `icons/` with its `icons/icons.md` row and "Used in" updated.
20. **Report:** list every file in `out/`, plus durations, loudness, choices made, lines worth re-recording, and anything you couldn't do. Then fold any lessons back into the toolkit `.md` files.
