# Stages

**Goal:** one Claude session per stage, not one per video. Context (and images) piles up over a whole video, and a 400K-token session re-reads all of it on every turn. Each stage starts clean and picks up from `log.md`.

| Stage | Steps (`/coding-video` numbering) | Ends with |
|---|---|---|
| 1 · Prep | Inspect/probe originals, identify talking-head recordings, mandatory voice-cleaning gate, then transcribe, then web captures from the script's list (`pipeline/web-capture.md`) (1–9) | handoff |
| 2 · Cut | take selection, rough cut (10–11) | handoff + **CHECKPOINT: wait for my OK** |
| 3 · Compose | storyboard with Creative take, composition, sound (`pipeline/sound.md`: sound map, cues, offline mix), render (12–13) | handoff |
| 4 · Deliver | subtitles, trailer (reels ≤ 2:59: 9:16 only, no 16:9 render, QA or stills; long-form: 16:9 + 9:16), QA, thumbnail, social copy, carousel (reels: `pipeline/carousel.md`, two approval stops), **save components** to `components/code/` (`CLAUDE.md`, Components), report (14–20), then the extra text posts (21, `pipeline/text-posts.md`, two approval stops; nothing above waits for them) | handoff + final report |

In Compose, be a creative co-director: script cues are the baseline, not a limit; improve them within the rules in `CLAUDE.md` (Creative direction), and list every creative change in `log.md`.

`/reel` uses the same stages and numbering. `/clipify` candidate picking is part of stage 2, but its dialogue-mode source transcript is also gated by `pipeline/voice-cleaning.md`. `/clipify` action mode does not use Whisper.

## Stage 1 · Prep execution order

**Before any Whisper/ASR on talking-head audio, pass the gate in `pipeline/voice-cleaning.md`. No exceptions without my explicit approval.** The gate file holds the full Prep order (probe → inventory → preflight → clean → report checks → listening → Whisper → transcript review → per-recording handoff table) and the failure handling.

## Delegation

**Delegation in every stage:** low-stakes tasks follow the chain in `pipeline/delegation.md` (Copilot → Codex → cursor-agent canary → Haiku); heavy jobs (renders, Whisper, final encodes, video-inspect, installs) go to the detached Haiku runner with `.status` files; creative and QA work stays with Claude. Prep: probing and proxies are low-stakes; voice-cleaning runs and transcription are heavy. Cut: only file moves are delegated. Compose: boilerplate, the SFX kit copy and the cue export are low-stakes, renders and the final mix are heavy, the sound map is yours. Deliver: SRT wrapping, social-copy scaffolding and `log.md` are low-stakes; final encodes and video-inspect are heavy; QA is yours.

## Starting a stage

- Before doing anything else, read `projects/<name>/project-state.json` (`vt-python tools/project_state.py show projects/<name>`) and only the latest `### Handoff` block and open issues in `log.md` (`grep -n '### Handoff' log.md`, then read from the last match), not the whole file. Then read the project files the stage depends on (`script.md`, `work/cutlist.md`, the EDL, `timeline.json`… as relevant), `brand.md` and this stage's `pipeline/` files. `CLAUDE.md` is already loaded; never Read it again.
- If the previous handoff has an unresolved open issue that blocks this stage, raise it with me first.
- Stage 3 never starts without my OK on the rough cut recorded in `log.md` as `**Approval:** rough_cut=approved` (and mirrored in `project-state.json` after `vt-python tools/project_state.py sync-handoff projects/<name>`).

## Ending a stage

- Write a handoff entry to `log.md` (format in `pipeline/project-log.md`): decisions and the reasons for them, rejected options, open issues, files produced, and next steps. Update `project-state.json` (`vt-python tools/project_state.py sync-handoff projects/<name>`) and optional `work/context/<stage>-context.md` (`pipeline/context-handoffs.md`).
- Write it so a fresh session with no memory of this one can continue without re-deriving anything: name exact files, timestamps, and parameter values.
- Then tell me the stage is done and to start the next one in a new session (`/clear`, then the next stage's prompt).

## Fallback

`/compact` only when a single stage genuinely outgrows a session (e.g. a long debugging run in stage 3). Write a handoff to `log.md` before compacting, so nothing is lost if the summary drops it.
