---
name: coding-video
description: Long-form (> 3:00) 16:9 coding video pipeline (tutorial or project demo) from raw talking-head and screen footage to a delivered MP4 with SRT. A coding video of ≤ 2:59 is a reel: 9:16 only.
argument-hint: <name>
---

# Coding video (16:9, 1920x1080, 30 fps; long-form > 3:00)

**Opener, close, pace and loudness: `CLAUDE.md` → House numbers.** Read only what the current stage needs (`pipeline/stages.md`).

**≤ 2:59 is a reel: 9:16 only.** Follow these stages, but frame, lay out, render, QA and thumbnail per `/reel`: no 16:9 output or `PresenterSplit`. The 16:9 steps below are long-form only.

## Brief rules (fixed for every video)

Prompts follow `templates/editing-prompt.md`. These rules apply without being repeated there; the prompt's notes win where more specific. `CLAUDE.md` (Quality bar, Creative direction) applies in full: it should feel like a premium explainer, not a slideshow.

- **Footage and layout.** Talking head is portrait phone video unless the prompt says otherwise. Every beat is HEAD, FULL or SPLIT (`brand.md` Layout, `components/specs/layout-states.md`); no default, mix all three. The script's `[B07 | mm:ss–mm:ss | STATE]` tags are the plan; switch points may move by a beat or two.
- **Script into the project.** The prompt's `# Script` → `projects/<name>/script.md` in the style of `templates/script-tutorial.md` or `templates/script-project-demo.md` (≤ 2:59: `templates/script-reel.md`), with a Glossary and beat IDs (add `B01…` if the prompt's script has none). A `# Hindi script` section is only saved, with `tools/twin/save_hindi_script.py`; do nothing else with it.
- **Caption prep (Prep).** In the `script.md` Glossary: caption spellings, number formatting (digits, ₹, %, separators) and orange-highlight words, from the prompt's notes, else derived from the script and listed in the handoff. Captions follow my actual words.
- **Web captures (Prep).** Take everything in `## Web captures` yourself (`pipeline/web-capture.md`).
- **Never cut any script line**, including one-word lines, the greeting, the recap and the sign-off. Only retakes, fillers and dead pauses go.
- **HARD RULE: length (final ≤ 2:59, or the prompt's limit).** In this order, stop at the first step that fits:
  1. Cut retakes: keep the last complete, clean take of each paragraph (`/cut-video`, `pipeline/take-selection.md`).
  2. Tighten pauses (House numbers); remove fillers and restarts; keep the deliberate pauses the script or prompt marks (e.g. around "Namoshkar!" and before the sign-off).
  3. Pitch-preserved speed-up from 1.05x in 0.05 steps, up to the prompt's cap, with the sync-safe chain (`setpts=PTS/k,fps=30` + `atempo=k`).
  4. Still over at the cap: **stop and ask me.** Never cut a line.

**Stage 1 · Prep** (steps 1–9). Probe every original source (`pipeline/probe-and-trim.md`; never modify `raw/` or `assets/`), then **Before any Whisper/ASR on talking-head audio, pass the gate in `pipeline/voice-cleaning.md`. No exceptions without my explicit approval.** It defines steps 2–9, through Whisper (`pipeline/transcribe.md`) and the handoff table. No cut selection with an unverified voice recording.

**Stage 2 · Cut**

10. **Take selection:** `pipeline/take-selection.md` with `/cut-video` (`balanced`; House numbers pauses and keep-last-take win). Write `work/cutlist.md`.
11. **CHECKPOINT:** 720p rough cut (talking head + verified audio) to `out/roughcut_preview.mp4`, with the cutlist summary, weak or missing lines, and the music pick or audition previews (`pipeline/music.md`). **Wait for my OK**; write the handoff.

**Stage 3 · Compose** (only after my OK is in `log.md`)

12. **Composition:** `pipeline/composition.md`. Storyboard by the `creative-director` subagent (`pipeline/composition.md`): scene table with measured length per beat plus the "Creative take" list. Then **3 approval stills** (the prompt's, else the hook frame and the two strongest beats); wait for my OK on any bigger change.
13. **Render:** `pipeline/render.md`.

**Stage 4 · Deliver**

14. **Subtitles:** `pipeline/subtitles.md`.
15. **Trailer:** `pipeline/trailer.md`. The prompt's `## 60-second cut` if given, else the default.
16. **QA:** `pipeline/qa.md` on the main video and every trailer; `vision-qa` looks at every sheet. Fix failures before reporting.
17. **Thumbnail:** `pipeline/thumbnail.md`. Always.
18. **Social copy:** `pipeline/social-copy.md` → `out/<name>_social.json`. A ≤ 2:59 video also gets `/carousel`.
19. **Save components:** `components/code/README.md`, Library rules; update "Used in" in `icons/icons.md`; with music, the checks and `finalize.py` in `pipeline/music.md`.
20. **Report:** files in `out/`, durations, loudness, choices, lines worth re-recording, anything not done. Fold lessons into the toolkit.
21. **Text posts (extra, after the report):** `/text-posts <name>` (its two approval stops).

## Deliverables (long-form)
- Long-form (> 3:00) keeps 16:9 + 9:16 as before: every long-form video ships with the main video, exactly one trailer cut rendered in landscape 16:9 and portrait 9:16 (a short cut defined in the prompt IS the trailer; otherwise the default from `pipeline/trailer.md`; never both), an SRT for each, thumbnails in `out/thumbnail/` along with a ChatGPT kit (up to 3 static assets plus a ready prompt and a template for my own) (`pipeline/thumbnail.md`), and `<name>_social.json` with ready-to-paste titles, posts and hashtags for LinkedIn, X, Instagram, Facebook, Threads and YouTube (`pipeline/social-copy.md`), and the text posts (`pipeline/text-posts.md`). Don't wait to be asked.

Project log every turn (`pipeline/project-log.md`).
