---
name: reel
description: 9:16 reel pipeline (1080x1920, 30–60 s) with a "Namoshkar!" opener, a hook landing within 3 s, big captions and fast pace.
argument-hint: <name>
---

# Reel (9:16, 1080x1920, 30 fps, 30–60 s)

**Read only what the current stage needs (`pipeline/stages.md`). `CLAUDE.md` is already loaded — never Read it again.**

Choose components from `components/index.md` first (rows: `grep -i '^| \[<Name>\]' components/index-full.md`); open only the specs you will use. If a component has saved code (✓), import it from `shared/` and set props. Logos come from `icons/` (look up with `grep -i '<brand>' icons/icons.md` (never Read it whole)).

Use the same four stages and delegation/vision rules as `/coding-video` (`pipeline/stages.md`, `pipeline/delegation.md`, `pipeline/video-inspect.md`). **Stage 1 · Prep runs in this exact order:**

1. Inspect and probe original footage (`pipeline/probe-and-trim.md`).
2. Inventory every talking-head recording and assign a unique ID.
3. Read `pipeline/voice-cleaning.md`, then run `vt-python tools/voice_preflight.py`. On `NOT READY`, stop and show me the `FAIL` lines and fixes; install nothing without my OK.
4. Run the cleaner once per recording, with unique output and report paths:
   ```bash
   vt-python tools/clean_audio.py "projects/<name>/raw/<recording>" \
     "projects/<name>/work/audio/cleaned/<recording-id>.wav" \
     --preset studio --mode quality \
     --report "projects/<name>/work/audio/reports/<recording-id>-clean-report.json"
   ```
   A non-zero exit fails the gate: read the `*.failed.json` and stop.
5. Inspect every report: `status: succeeded` with the same `run_id` as `<wav>.run-status.json`, source/output identity, duration delta, LUFS, true peak, clipping flags and `warnings` (`pipeline/voice-cleaning.md`, Required report checks).
6. Require `mode: quality`, `stages.wpe: processed` and `stages.deepfilternet3: processed` (model `DeepFilterNet3`, device recorded), and `production_gate.automated_checks_passed: true` for every recording.
7. Listen to each original/cleaned pair at matched loudness and verify echo, hiss, clarity, natural voice, artifacts and sync, unless the approved-setup exemption in `pipeline/voice-cleaning.md` applies (approved setup, passing report and tone check; log it).
8. Only after all recordings pass, run Whisper on the corresponding verified cleaned WAVs (`pipeline/transcribe.md`).
9. Review each transcript and its timestamps, then continue the remaining Prep and log the per-recording table (source → cleaned WAV → report/run_id → stage statuses → listening result → transcript).

If cleaning fails, stop and report it; do not switch modes or transcribe original audio without explicit approval. If listening is unavailable, disclose that limitation and request explicit approval before Whisper. Keep reports separate; no reel candidate search or editing may use a transcription that bypassed this gate. `/clipify`, `/cut-video` and `/add-zooms` reuse these verified WAVs; they don't clean again.

## Brief rules (fixed for every video; the prompt adds only the specifics)

Prompts follow `templates/editing-prompt.md` (topic, path, speed-up cap, notes/special assets, `# Script`, `## 60-second cut`). Everything below applies without being repeated in the prompt; the prompt's notes win where they are more specific.

- **Quality bar.** `CLAUDE.md` → Quality bar, with no exceptions. The video should feel like a premium explainer, not a slideshow.
- **Footage and layout.** Talking head is portrait phone video unless the prompt says otherwise. Every beat is HEAD, FULL or SPLIT (`brand.md` Layout, `components/specs/layout-states.md`); the script's state tags are the plan, and switch points may move by a beat or two (`CLAUDE.md`, Creative direction). In SPLIT the graphic sits on top and the face is docked below.
- **Script into the project.** Save the prompt's `# Script` as `projects/<name>/script.md` in the style of `templates/script-reel.md`, with a Glossary.
- **Caption prep (Prep).** Record in the `script.md` Glossary: caption spellings (names, APIs and code terms exactly as written), number formatting (spoken numbers → digits, ₹, %, separators) and the orange-highlight words. Take them from the prompt's notes; where it gives none, derive them from the script and list them in the handoff. Captions follow the actual words (`CLAUDE.md`, Workflow).
- **Never cut any script line**, including one-word lines, the greeting, the recap and the sign-off. Only retakes, fillers and dead pauses go.
- **HARD RULE: length (final ≤ 2:59, or the prompt's limit).** In this order, and stop at the first step that fits:
  1. Cut retakes: keep the last complete, clean take of each paragraph (`/cut-video`, `pipeline/take-selection.md`).
  2. Tighten pauses to 0.2–0.3 s and remove fillers and restarts. Keep the deliberate pauses the script or prompt marks (e.g. after "Namoshkar!", before "Bye bye, sayonara!"). A 30–60 s reel uses the tighter pauses under Length below.
  3. Still over: pitch-preserved speed-up from 1.05x, rising in 0.05 steps, up to the prompt's cap. Use the sync-safe chain (`setpts=PTS/k,fps=30` + `atempo=k`, `pipeline/qa.md`).
  4. Still over at the cap: **stop and ask me.** Never cut a line.
- **Checkpoints.**
  1. Stages, one session each (`pipeline/stages.md`): Prep (voice gate → Whisper → handoff) · Cut (take selection + rough cut; report measured length and speed-up factor; **stop for my OK**) · Compose (storyboard, build, render) · Deliver.
  2. Storyboard: a scene table with measured length per beat, plus the "Creative take" list (idea, beat, why). Then **3 approval stills** (the prompt names them; otherwise the hook frame and the two strongest beats); wait for my OK on any bigger change.
  3. Build scene by scene, render through `gpu-run`, run video-inspect (`--thorough` on the final) and QA (`pipeline/qa.md`).
  4. Deliver: main `out/<name>_9x16.mp4` + SRT; trailer = the prompt's `## 60-second cut` if given, else the default (`pipeline/trailer.md`), 9:16 + SRT; cover/thumbnail + ChatGPT kit (`pipeline/thumbnail.md`); `<name>_social.json` (`pipeline/social-copy.md`); carousel twin (`/carousel`).
  5. Save components (`CLAUDE.md`, Components → Deliver) and apply any series-file update the prompt asks for.
  6. Project log every turn (`pipeline/project-log.md`).

- **Skills.** Cut with `/cut-video` (`aggressive` tone, but this file's pause lengths win), and punch in with `/add-zooms` (punches and ratchets only). If the source is a long video, use `/clipify` (dialogue mode) to pick 3–5 candidate moments. Show them to me, then build each chosen one as a reel with the rules below.

- **Opener and hook.** Open with "Namoshkar!" (~1.5 s with the pause), then the hook line: the boldest claim or result, starting by ~1.5 s and landing within 3 s. A big text hook (2–5 words) is on screen from frame 0, so muted viewers get the hook while I greet. If the strongest line is mid-recording, move it right after "Namoshkar!".
- **Length 30–60 s.** Cut to one idea. Tighten pauses harder: about 0.10 s between phrases and 0.15 s between sentences.
- **Fast pace.** The visual changes every 1.5–3 s (punch-in, a screen, a graphic, a card). No beat holds still.
- **Layout.** There is no default layout. Every beat is HEAD (my face fills the frame), FULL (graphic fills the frame, my face hidden, voice continues) or SPLIT (graphic on top, me docked below), per `brand.md` Layout and `components/specs/layout-states.md`. Read the script's `[mm:ss–mm:ss | HEAD|FULL|SPLIT]` tags as the plan, mix all three, and switch by hard cut or brand wipe only where a concept starts or ends. HEAD uses the portrait recording natively. Keep the face out of the top ~12% and bottom ~20% UI zones.
- **Creative direction.** Script cues are the baseline, not a limit: bring a better visual take where it explains better, within the rules in `CLAUDE.md` (never change spoken lines, facts or code, `brand.md`, the length limit, or a cue's intent). List a "Creative take" in the storyboard; small changes just do and log, bigger ones go to 3 approval stills for my OK.
- **Playlists.** If the project sits in a playlist (`projects/<playlist>/<NN>-<topic>/`), also follow `series/<playlist>.md`.
- **Big captions.** See `components/specs/Captions.md` (reel mode): 1–3 words at a time, ~80 px, placed per state (HEAD lower third clear of the face, SPLIT in the strip, FULL in a band clear of the graphic's key element).
- **Safe zones.** Keep text clear of the right ~15% (platform buttons) and the bottom ~20% (description overlay).
- **Ending.** A one-line recap (the payoff of the hook), then "Bye bye, sayonara!" with a wave. A short `EndCard` (≤ 2 s) may follow.
- **Deliver.** `out/<name>_9x16.mp4` plus an SRT, at -14 to -16 LUFS. Always make a cover/thumbnail with `pipeline/thumbnail.md`: 1080x1920 only, no 1280x720. Then save new or extended components to `components/code/` and update `icons/icons.md` "Used in" (`CLAUDE.md`, Icons and Components).
- **9:16 only.** A reel never builds, previews, stills, QAs or renders anything in 16:9: no landscape layout, composition, trailer or thumbnail (`CLAUDE.md`, Deliverables).
- **Trailer.** Always make exactly one short cut, rendered in 9:16 only: `out/<name>_trailer_9x16.mp4` (`pipeline/trailer.md`). If the prompt defines a short cut, that is the trailer; otherwise the default 15–20 s trailer. Never both.
- **Carousel twin.** After the final render's QA, run `/carousel <name>` (`pipeline/carousel.md`): 6–8 slides in `out/carousel/`, with its outline and slide-1 approval stops.
- **Social copy.** Always write `out/<name>_social.json` per `pipeline/social-copy.md`. YouTube chapters don't apply to a reel; use the `shorts_title` and a short description instead.

Stop at the rough cut for my OK, as always.
