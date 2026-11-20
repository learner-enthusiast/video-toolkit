# Stages

**Goal:** one Claude session per stage, not one per video. Context (and images) piles up over a whole video, and a 400K-token session re-reads all of it on every turn. Each stage starts clean and picks up from `log.md`.

| Stage | Steps (`/coding-video` numbering) | Ends with |
|---|---|---|
| 1 · Prep | Inspect/probe originals, identify talking-head recordings, mandatory voice-cleaning gate, then transcribe (1–9) | handoff |
| 2 · Cut | take selection, rough cut (10–11) | handoff + **CHECKPOINT: wait for my OK** |
| 3 · Compose | storyboard with Creative take, composition, sound (`pipeline/sound.md`: sound map, cues, offline mix), render (12–13) | handoff |
| 4 · Deliver | subtitles, trailer (reels ≤ 2:59: 9:16 only, no 16:9 render, QA or stills; long-form: 16:9 + 9:16), QA, thumbnail, social copy, carousel (reels: `pipeline/carousel.md`, two approval stops), **save components** to `components/code/` (`CLAUDE.md`, Components), report (14–20) | handoff + final report |

In Compose, be a creative co-director: script cues are the baseline, not a limit; improve them within the rules in `CLAUDE.md` (Creative direction), and list every creative change in `log.md`.

`/reel` uses the same stages and numbering. `/clipify` candidate picking is part of stage 2, but its dialogue-mode source transcript is also gated by `pipeline/voice-cleaning.md`. `/clipify` action mode does not use Whisper. `/cut-video`, `/clipify` and `/add-zooms` reuse the Prep-verified cleaned WAV; they run the gate themselves only when invoked standalone.

## Stage 1 · Prep execution order

Follow this sequence exactly. **No Whisper transcription of source talking-head audio may start before steps 1–7 are complete for every relevant recording.** This gate applies to `/coding-video`, `/reel`, `/cut-video`, `/add-zooms`, and `/clipify` dialogue/hybrid modes.

1. **Inspect and probe originals.** Read the project log and source files; run the original-footage checks in `pipeline/probe-and-trim.md`. Do not modify `raw/` or `assets/`.
2. **Identify recordings.** Inventory every relevant talking-head recording/audio stream and assign each a stable, unique recording ID. Record the source path and intended cleaned output path.
3. **Read `pipeline/voice-cleaning.md` and run the preflight.** It is the execution and approval gate for all talking-head source audio. Run `vt-python tools/voice_preflight.py`; on `NOT READY`, stop and report its `FAIL` lines and fixes before cleaning anything.
4. **Clean each recording.** Run the Studio/quality command from that guide once per source recording (`work/audio/cleaned/<recording-id>.wav`, `work/audio/reports/<recording-id>-clean-report.json`). A non-zero exit fails the gate. Never overwrite raw footage or another recording's output/report.
5. **Inspect every report.** Confirm each report exists, parses, has `status: succeeded`, matches the `run_id` in `<wav>.run-status.json`, and names the intended source and output. Review duration delta, input/output loudness and true peak, clipping flags and `warnings` (`pipeline/voice-cleaning.md`, Required report checks).
6. **Confirm required stages.** For each report, verify `mode: quality`, `stages.wpe: processed` (`dereverberation.applied: true`), `stages.deepfilternet3: processed` with model `DeepFilterNet3`, its backend and device, and `production_gate.automated_checks_passed: true`. Any failed, not_attempted, disabled, missing, or ambiguous stage fails the gate.
7. **Listen and verify each pair.** Compare original and cleaned audio for room echo/reverb, hiss, speech clarity, natural voice identity, pitch/timbre/dynamics, clipping/distortion/artifacts, loudness and sync. If the current environment cannot listen to both recordings, disclose that limitation and ask for explicit approval before transcription. Exception: a recording from an approved setup with a passing report and tone check skips this stop (`pipeline/voice-cleaning.md`, Approved-setup exemption); log it.
8. **Transcribe only verified cleaned audio.** Run `pipeline/transcribe.md` and the applicable ASR step using the cleaned path recorded for that source, never the original or an unverified proxy/extraction. Run GPU preflight from `pipeline/gpu.md` immediately before Whisper if it has not already passed.
9. **Continue the remaining Prep workflow.** Review each transcript and its word timestamps (`pipeline/transcribe.md`, Checks), copy the verified WAV to `work/audio/clean.wav` if a single canonical voice path is needed, finish remaining prep artifacts, and write the Stage 1 handoff with the per-recording table (source → cleaned WAV → report/run_id → stage statuses → listening result → transcript) from `pipeline/voice-cleaning.md`. Cut (stage 2) may not start on a recording missing from that table.

### Quality-gate failure handling

- If the cleaner exits unsuccessfully, WPE or DeepFilterNet 3 fails or is skipped, a report is missing/invalid, or quality/synchronization is not verified, stop Prep before Whisper. Report the specific recording, stage, report/error and next blocking action.
- Do not switch modes, bypass the cleaner, use the original for ASR, or route around the gate through another skill. Any substitute processing requires the user's explicit approval.
- If listening is unavailable, say so and request approval. Do not treat numeric measurements or successful execution as listening approval.
- Resume transcription only after the required stages pass and listening is completed, or the user explicitly approves a documented exception.

## Delegation

**Delegation in every stage:** low-stakes tasks follow the chain in `pipeline/delegation.md` (Copilot → Codex → cursor-agent canary → Haiku); heavy jobs (renders, Whisper, final encodes, video-inspect, installs) go to the detached Haiku runner with `.status` files; creative and QA work stays with Claude. Prep: probing and proxies are low-stakes; voice-cleaning runs and transcription are heavy. Report inspection, listening and the gate decision remain Claude's responsibility; do not launch Whisper as a delegated job until Claude records that every source has passed the gate. Cut: only file moves are delegated. Compose: boilerplate, the SFX kit copy and the cue export are low-stakes, renders and the final mix are heavy, the sound map is yours. Deliver: SRT wrapping, social-copy scaffolding and `log.md` are low-stakes; final encodes and video-inspect are heavy; QA is yours.

## Starting a stage

- Before doing anything else, read only the latest `### Handoff` block and the open issues in `log.md` (`grep -n '### Handoff' log.md`, then read from the last match), not the whole file. Then read the project files the stage depends on (`script.md`, `work/cutlist.md`, the EDL, `timeline.json`… as relevant), `brand.md` and this stage's `pipeline/` files. `CLAUDE.md` is already loaded; never Read it again.
- If the previous handoff has an unresolved open issue that blocks this stage, raise it with me first.
- Stage 3 never starts without my OK on the rough cut recorded in `log.md`.

## Ending a stage

- Write a handoff entry to `log.md` (format in `pipeline/project-log.md`): decisions and the reasons for them, rejected options, open issues, files produced, and next steps.
- Write it so a fresh session with no memory of this one can continue without re-deriving anything: name exact files, timestamps, and parameter values.
- Then tell me the stage is done and to start the next one in a new session (`/clear`, then the next stage's prompt).

## Fallback

`/compact` only when a single stage genuinely outgrows a session (e.g. a long debugging run in stage 3). Write a handoff to `log.md` before compacting, so nothing is lost if the summary drops it.
