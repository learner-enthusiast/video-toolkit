---
name: reel
description: 9:16 reel pipeline (1080x1920) for any video whose final length is ≤ 2:59. Hook first, then the greeting, with big captions and fast pace.
argument-hint: <name>
---

# Reel (9:16, 1080x1920, 30 fps)

**Length, pace, opener, close and loudness: `CLAUDE.md` → House numbers.** Read only what the current stage needs (`pipeline/stages.md`).

**Stage 1 · Prep:** probe the footage (`pipeline/probe-and-trim.md`), then **Before any Whisper/ASR on talking-head audio, pass the gate in `pipeline/voice-cleaning.md`. No exceptions without my explicit approval.** It has the exact `clean_audio.py` command. Then Whisper on the verified WAVs (`pipeline/transcribe.md`) and the per-recording handoff table; `/clipify`, `/cut-video` and `/add-zooms` reuse those WAVs.

## Brief rules (fixed for every video)

Prompts follow `templates/editing-prompt.md`. These rules apply without being repeated there; the prompt's notes win where more specific. `CLAUDE.md` (Quality bar, Creative direction) applies in full: it should feel like a premium explainer, not a slideshow.

- **Footage and layout.** Talking head is portrait phone video unless the prompt says otherwise. Every beat is HEAD, FULL or SPLIT (`brand.md` Layout, `components/specs/layout-states.md`); no default, mix all three. The script's `[B07 | mm:ss–mm:ss | STATE]` tags are the plan; switch points may move by a beat or two. HEAD uses the portrait recording natively; keep the face out of the top ~12% and bottom ~20%. Switch by hard cut or brand wipe only where a concept starts or ends.
- **Script into the project.** The prompt's `# Script` → `projects/<name>/script.md` in the style of `templates/script-reel.md`, with a Glossary and beat IDs (add `B01…` if the prompt's script has none).
- **Caption prep (Prep).** In the `script.md` Glossary: caption spellings, number formatting (digits, ₹, %, separators) and orange-highlight words, from the prompt's notes, else derived from the script and listed in the handoff. Captions follow my actual words.
- **Web captures (Prep).** Take everything in `## Web captures` yourself (`pipeline/web-capture.md`). Frame FULL beats with a mobile viewport.
- **Never cut any script line**, including one-word lines, the greeting, the recap and the sign-off. Only retakes, fillers and dead pauses go.
- **HARD RULE: length (final ≤ 2:59, or the prompt's limit).** In this order, stop at the first step that fits:
  1. Cut retakes: keep the last complete, clean take of each paragraph (`/cut-video`, `pipeline/take-selection.md`).
  2. Tighten pauses (House numbers); remove fillers and restarts; keep the deliberate pauses the script or prompt marks (e.g. around "Namoshkar!" and before the sign-off).
  3. Pitch-preserved speed-up from 1.05x in 0.05 steps, up to the prompt's cap, with the sync-safe chain (`setpts=PTS/k,fps=30` + `atempo=k`).
  4. Still over at the cap: **stop and ask me.** Never cut a line.
- **Opener and hook.** House numbers. The hook line is the boldest claim or result; the on-screen text hook is 2–5 words. If the strongest line is mid-recording, move it to the very start.
- **Fast pace.** The visual changes every 1.5–3 s. No beat holds still.
- **Captions.** `components/specs/Captions.md` (reel mode): 1–3 words, ~80 px, placed per state. Text stays clear of the right ~15% and bottom ~20%.
- **Ending.** The House numbers close (the recap pays off the hook); an `EndCard` ≤ 2 s may follow.
- **Playlists.** Also follow `series/<playlist>.md`.
- **Skills.** Cut with `/cut-video` (`aggressive`; House numbers pauses win); punch with `/add-zooms` (punches and ratchets only). For a long source, ask me to run `/clipify` (I start it; dialogue mode) for 3–5 candidates, show them, then build each chosen one.

## Checkpoints
1. One session per stage: Prep · Cut (take selection + rough cut; report length and speed-up; **stop for my OK**) · Compose · Deliver.
2. Storyboard by the `creative-director` subagent (`pipeline/composition.md`): scene table with measured length per beat plus the "Creative take" list. Then **3 approval stills** (the prompt's, else the hook frame and the two strongest beats); wait for my OK on any bigger change.
3. Build scene by scene, render through `gpu-run`, then video-inspect (`--thorough` on the final) and QA (`pipeline/qa.md`).
4. Deliver, **9:16 only** (never build, still, QA or render 16:9):
   - `out/<name>_9x16.mp4` + SRT at House numbers loudness.
   - Exactly one trailer, `out/<name>_trailer_9x16.mp4` + SRT: the prompt's `## 60-second cut` if given, else the default 15–20 s one (`pipeline/trailer.md`).
   - Cover 1080x1920 + ChatGPT kit (`pipeline/thumbnail.md`).
   - `out/<name>_social.json` (`pipeline/social-copy.md`; no YouTube chapters: `shorts_title` and a short description).
   - Carousel twin after final QA: `/carousel <name>` (its two approval stops).
5. Save components (`components/code/README.md`, Library rules), update "Used in" in `icons/icons.md`, apply any series-file update the prompt asks for.
6. Last, after reporting: text posts (extra) with `/text-posts <name>` (its approval stops).
7. Project log every turn (`pipeline/project-log.md`).
