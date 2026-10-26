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
5. **Take selection:** `pipeline/take-selection.md`. Write `work/cutlist.md`.
6. **CHECKPOINT:** render a 720p rough cut (talking head + clean audio) to `out/roughcut_preview.mp4`. Show me the cutlist summary and any weak or missing lines. **Wait for my OK.**
7. **Composition:** `pipeline/composition.md`. Choose the framing: crop if the source is ≥ 1440 px wide, otherwise `components/PresenterSplit.md`. Tell me which and why.
8. **Render:** `pipeline/render.md`.
9. **Subtitles:** `pipeline/subtitles.md`.
10. **QA:** `pipeline/qa.md`. Fix what fails before reporting.
11. **Thumbnail:** `pipeline/thumbnail.md`, if I asked for one.
12. **Report:** durations, loudness, choices made, lines worth re-recording, and anything you couldn't do. Then fold any lessons back into the toolkit `.md` files.

If a trailer or reel cut is also needed, build it from the same timeline and follow `/reel` for the 9:16 rules.
