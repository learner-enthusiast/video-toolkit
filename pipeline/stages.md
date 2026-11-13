# Stages

**Goal:** one Claude session per stage, not one per video. Context (and images) piles up over a whole video, and a 400K-token session re-reads all of it on every turn. Each stage starts clean and picks up from `log.md`.

| Stage | Steps (`/coding-video` numbering) | Ends with |
|---|---|---|
| 1 · Prep | GPU, probe and trim, clean audio, transcribe (1–4) | handoff |
| 2 · Cut | take selection, rough cut (5–6) | handoff + **CHECKPOINT: wait for my OK** |
| 3 · Compose | storyboard with Creative take, composition, render (7–8) | handoff |
| 4 · Deliver | subtitles, trailers, QA, thumbnail, social copy, carousel (reels: `pipeline/carousel.md`, two approval stops), report (9–14) | handoff + final report |

In Compose, be a creative co-director: script cues are the baseline, not a limit; improve them within the rules in `CLAUDE.md` (Creative direction), and list every creative change in `log.md`.

`/reel` uses the same stages. `/clipify` candidate picking is part of stage 2.

**Starting a stage**
- Before doing anything else, read `projects/<name>/log.md` (at least the latest handoff and every open issue), then the project files the stage depends on (`script.md`, `work/cutlist.md`, the EDL, `timeline.json`… as relevant), plus `CLAUDE.md`, `brand.md` and this stage's `pipeline/` files.
- If the previous handoff has an unresolved open issue that blocks this stage, raise it with me first.
- Stage 3 never starts without my OK on the rough cut recorded in `log.md`.

**Ending a stage**
- Write a handoff entry to `log.md` (format in `pipeline/project-log.md`): decisions and the reasons for them, rejected options, open issues, files produced, and next steps.
- Write it so a fresh session with no memory of this one can continue without re-deriving anything: name exact files, timestamps, and parameter values.
- Then tell me the stage is done and to start the next one in a new session (`/clear`, then the next stage's prompt).

**Fallback**
- `/compact` only when a single stage genuinely outgrows a session (e.g. a long debugging run in stage 3). Write a handoff to `log.md` before compacting, so nothing is lost if the summary drops it.
