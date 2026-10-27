---
name: coding-video
description: 16:9 coding video pipeline (tutorial or project demo) from raw talking-head and screen footage to a delivered MP4 with SRT.
argument-hint: <name>
---

# Coding video (16:9, 1920x1080, 30 fps)

Work in `projects/<name>/`. Read `CLAUDE.md` and `brand.md` first. Follow each step's file in `pipeline/`.

1. **GPU:** `pipeline/gpu.md`. Do not continue until the checks pass.
2. **Probe and trim:** `pipeline/probe-and-trim.md`. Report every file's resolution, rotation, fps and duration.
3. **Clean audio:** `pipeline/clean-audio.md`.
4. **Transcribe:** `pipeline/transcribe.md`.
5. **Take selection:** `pipeline/take-selection.md`, using `/cut-video` as the cutting engine (MFA word boundaries, ground-truthed windows, trim+concat render) with `balanced` tone. The pause lengths and the keep-last-take rule in `take-selection.md` win. Write `work/cutlist.md`.
6. **CHECKPOINT:** render a 720p rough cut (talking head + clean audio) to `out/roughcut_preview.mp4`. Show me the cutlist summary and any weak or missing lines. **Wait for my OK.**
7. **Composition:** `pipeline/composition.md`. Choose the framing: crop if the source is ≥ 1440 px wide, otherwise `components/PresenterSplit.md`. Tell me which and why. Use `/add-zooms` to write the punch/ratchet map from the word timestamps. It decides where the ~108% framing lands to hide each jump cut, and those zooms are applied in the composition. No Ken Burns from add-zooms: do slow pushes in Remotion with ease-in-out.
8. **Render:** `pipeline/render.md`.
9. **Subtitles:** `pipeline/subtitles.md`.
10. **Trailers:** `pipeline/trailer.md`. Always make both: `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`.
11. **QA:** `pipeline/qa.md`, on the main video and both trailers. Fix what fails before reporting.
12. **Thumbnail:** `pipeline/thumbnail.md`. Always.
13. **Social copy:** `pipeline/social-copy.md`. Always write `out/<name>_social.json`.
14. **Report:** list every file in `out/`, plus durations, loudness, choices made, lines worth re-recording, and anything you couldn't do. Then fold any lessons back into the toolkit `.md` files.
