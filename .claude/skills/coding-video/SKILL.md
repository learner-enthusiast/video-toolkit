---
name: coding-video
description: Long-form (> 3:00) 16:9 coding video pipeline (tutorial or project demo) from raw talking-head and screen footage to a delivered MP4 with SRT. A coding video of ≤ 2:59 is a reel: 9:16 only.
argument-hint: <name>
---

# Coding video (16:9, 1920x1080, 30 fps; long-form > 3:00)

**Read only what the current stage needs (`pipeline/stages.md`). `CLAUDE.md` is already loaded — never Read it again.**

**Short coding videos (final length ≤ 2:59) are reels: 9:16 only (1080x1920).** Follow the stages below, but frame, lay out, render, QA and thumbnail everything per `/reel` and `components/specs/layout-states.md` in 9:16. No 16:9 main, trailer, thumbnail, stills or `PresenterSplit`. The 16:9 steps below apply to long-form only.

Work in `projects/<name>/` (or `projects/<playlist>/<NN>-<topic>/` for a playlist episode; then also follow `series/<playlist>.md`). Read `brand.md` first (`CLAUDE.md` is already loaded). Logos come from `icons/` (look up with `grep -i '<brand>' icons/icons.md` (never Read it whole); download an official one into `icons/` only if missing). Choose components from `components/index.md` first (rows: `grep -i '^| \[<Name>\]' components/index-full.md`); open only the specs you will use. Follow each step's file in `pipeline/`.

Run this as four stages, one session each (`pipeline/stages.md`). Start each stage from the latest `### Handoff` in `log.md` (`pipeline/stages.md`, Starting a stage), and end it with a handoff in `log.md`. Shell work goes to Haiku as exact-command batches (`pipeline/delegation.md`). Vision goes through contact sheets (`pipeline/video-inspect.md`).

## Brief rules (fixed for every video; the prompt adds only the specifics)

Prompts follow `templates/editing-prompt.md` (topic, path, speed-up cap, notes/special assets, `# Script`, `## 60-second cut`). Everything below applies without being repeated in the prompt; the prompt's notes win where they are more specific.

- **House numbers.** Opener, close, pace and loudness: `CLAUDE.md` → House numbers.
- **Quality bar.** `CLAUDE.md` → Quality bar, with no exceptions. The video should feel like a premium explainer, not a slideshow.
- **Footage and layout.** Talking head is portrait phone video unless the prompt says otherwise. Every beat is HEAD, FULL or SPLIT (`brand.md` Layout, `components/specs/layout-states.md`); the script's state tags are the plan, and switch points may move by a beat or two (`CLAUDE.md`, Creative direction). In SPLIT the graphic sits on top and the face is docked below.
- **Script into the project.** Save the prompt's `# Script` as `projects/<name>/script.md` in the style of `templates/script-tutorial.md` or `templates/script-project-demo.md` (≤ 2:59: `templates/script-reel.md`), with a Glossary.
- **Caption prep (Prep).** Record in the `script.md` Glossary: caption spellings (names, APIs and code terms exactly as written), number formatting (spoken numbers → digits, ₹, %, separators) and the orange-highlight words. Take them from the prompt's notes; where it gives none, derive them from the script and list them in the handoff. Captions follow the actual words (`CLAUDE.md`, Workflow).
- **Web captures (Prep).** Take every capture in the script's `## Web captures` list yourself with Playwright (`pipeline/web-capture.md`): framed for its beat, cleaned, focus boxes saved. Never ask me for public pages.
- **Never cut any script line**, including one-word lines, the greeting, the recap and the sign-off. Only retakes, fillers and dead pauses go.
- **HARD RULE: length (final ≤ 2:59, or the prompt's limit).** In this order, and stop at the first step that fits:
  1. Cut retakes: keep the last complete, clean take of each paragraph (`/cut-video`, `pipeline/take-selection.md`).
  2. Tighten pauses (`CLAUDE.md` → House numbers) and remove fillers and restarts. Keep the deliberate pauses the script or prompt marks (e.g. after "Namoshkar!", before "Bye bye, sayonara!").
  3. Still over: pitch-preserved speed-up from 1.05x, rising in 0.05 steps, up to the prompt's cap. Use the sync-safe chain (`setpts=PTS/k,fps=30` + `atempo=k`, `pipeline/qa.md`).
  4. Still over at the cap: **stop and ask me.** Never cut a line.
- **Checkpoints.**
  1. Stages, one session each (`pipeline/stages.md`): Prep (voice gate → Whisper → handoff) · Cut (take selection + rough cut; report measured length and speed-up factor; **stop for my OK**) · Compose (storyboard, build, render) · Deliver.
  2. Storyboard (by the `creative-director` subagent, `pipeline/composition.md`): a scene table with measured length per beat, plus the "Creative take" list (idea, beat, why). Then **3 approval stills** (the prompt names them; otherwise the hook frame and the two strongest beats); wait for my OK on any bigger change.
  3. Build scene by scene, render through `gpu-run`, run video-inspect (`--thorough` on the final) and QA (`pipeline/qa.md`).
  4. Deliver: per `CLAUDE.md` → Deliverables (long-form: 16:9 + 9:16 main and trailer; ≤ 2:59: 9:16 only); trailer = the prompt's `## 60-second cut` if given, else the default (`pipeline/trailer.md`); SRT for each; thumbnail + ChatGPT kit; `<name>_social.json`; carousel twin for every 9:16 delivery.
  5. Save components (`CLAUDE.md`, Components → Deliver) and apply any series-file update the prompt asks for.
  6. Project log every turn (`pipeline/project-log.md`).

**Stage 1 · Prep** (steps 1–9)

1–9. Probe every original source (`pipeline/probe-and-trim.md`: resolution, rotation, fps, duration, audio streams; never modify `raw/` or `assets/`), then **Before any Whisper/ASR on talking-head audio, pass the gate in `pipeline/voice-cleaning.md`. No exceptions without my explicit approval.** It defines steps 2–9 (inventory, preflight, cleaning with `vt-python tools/clean_audio.py "projects/<name>/raw/<recording>" "projects/<name>/work/audio/cleaned/<recording-id>.wav" --preset studio --mode quality --report "projects/<name>/work/audio/reports/<recording-id>-clean-report.json"`, report checks, listening, Whisper via `pipeline/transcribe.md`, transcript review, the per-recording handoff table). `/coding-video` may not proceed to cut selection with an unverified voice recording.

**Stage 2 · Cut** (steps 10–11)

10. **Take selection:** `pipeline/take-selection.md`, using `/cut-video` as the cutting engine (MFA word boundaries, ground-truthed windows, trim+concat render) with `balanced` tone. The House numbers pause lengths and the keep-last-take rule in `take-selection.md` win. Write `work/cutlist.md`.
11. **CHECKPOINT:** render a 720p rough cut (talking head + verified clean audio) to `out/roughcut_preview.mp4`. Show me the cutlist summary and any weak or missing lines. **Wait for my OK.** Write the handoff and end the session here.

**Stage 3 · Compose** (steps 12–13; only after my OK is recorded in `log.md`)

12. **Composition:** `pipeline/composition.md`. Lay every beat out as HEAD, FULL or SPLIT (`brand.md` Layout, `components/specs/layout-states.md`; no default, mix all three, read the script's `[mm:ss–mm:ss | STATE]` tags as the plan). For HEAD framing: crop if the source is ≥ 1440 px wide, otherwise `components/specs/PresenterSplit.md`. Tell me which and why. Be a creative co-director: cues are the baseline, bring a better take within the rules in `CLAUDE.md` (Creative direction); write a "Creative take" list in `work/storyboard.md`, do small improvements and log them, and show bigger changes in 3 approval stills for my OK. Use `/add-zooms` to write the punch/ratchet map from the word timestamps. It decides where the ~108% framing lands to hide each jump cut, and those zooms are applied in the composition. No Ken Burns from add-zooms: do slow pushes in Remotion with ease-in-out.
13. **Render:** `pipeline/render.md`.

**Stage 4 · Deliver** (steps 14–21)

14. **Subtitles:** `pipeline/subtitles.md`.
15. **Trailer:** `pipeline/trailer.md`. Long-form: always make both `out/<name>_trailer_16x9.mp4` and `out/<name>_trailer_9x16.mp4`. A ≤ 2:59 video: `out/<name>_trailer_9x16.mp4` only.
16. **QA:** `pipeline/qa.md`, on the main video and every trailer render. Every contact sheet is looked at by the vision subagent (`pipeline/video-inspect.md`, Vision subagent) before delivering. Fix what fails before reporting.
17. **Thumbnail:** `pipeline/thumbnail.md`. Always.
18. **Social copy:** `pipeline/social-copy.md`. Always write `out/<name>_social.json`.
19. **Save components:** `CLAUDE.md` (Components, Deliver): clean up every new or extended component that worked, save it to `components/code/` with a `preview.png`, update its spec, its `components/index-full.md` row and the ✓ in `components/index.md`, set `last_used` on every component the video used. Logos: confirm every icon used is in `icons/` with its `icons/icons.md` row and "Used in" updated.
20. **Report:** list every file in `out/`, plus durations, loudness, choices made, lines worth re-recording, and anything you couldn't do. Then fold any lessons back into the toolkit `.md` files.
21. **Text posts (extra, after the report):** `/text-posts <name>` (`pipeline/text-posts.md`): the LinkedIn hook photo + post, the X post and the X Article in `out/text-posts/`, with its two approval stops. The video's LinkedIn/X captions in the social JSON stay as they are.
