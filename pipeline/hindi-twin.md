# Hindi twin

**Goal:** the Hindi version of a delivered English video, made from the **same composition**: same slides, components, English on-screen text, layout states and sound design. Only the voice, the face footage, the cue times and the captions change. Captions are Roman Hindi made by tools; Claude never writes or edits caption text, transliterations or dictionary entries.

**Rules that stay the same:** `CLAUDE.md` (House numbers: opener, close, pauses, length ≤ 2:59, loudness), the voice-cleaning gate, the rough-cut stop, and a fresh final visual QA.

**Deliverables, exactly four:** `out/<stem>-hi_9x16.mp4` + `.srt` and `out/<stem>-hi_trailer_9x16.mp4` + `.srt` (`<stem>` = the English main's name). **No** social JSON, thumbnail, carousel, text posts, ChatGPT kit or new components: never run `/carousel`, `/text-posts`, the thumbnail or social-copy steps.

Tool paths are relative to the toolkit root; commands run from the twin's `work/` unless shown otherwise.

## Setup
- Project: `projects/<name>-hi/` (playlist: `projects/<playlist>/<NN>-<topic>-hi/`), from `vt-python tools/twin/new_twin.py projects/<name>` (or `/new-video <name>-hi --twin-of <name>`). The Hindi recording goes in its own `raw/`.
- Script: the English prompt's `# Hindi script` section is saved during the English Prep with `tools/twin/save_hindi_script.py` (nothing else happens then). A separate Hindi prompt (`templates/editing-prompt-hindi.md`) is saved the same way.
- **Gate:** `vt-python tools/twin/gate.py projects/<name>-hi` must exit 0 before anything else. It needs the English final approval and a passed final QA in its `log.md`, the delivered main, named cues, a trailer that reads `trailer_ranges.json`, and every cue's beat in the Hindi script. If it refuses, stop and tell me why.

## H1 · Prep + Cut (`project_state.py set-stage <twin> cut`)
1. Probe, then the voice-cleaning gate (`pipeline/voice-cleaning.md`, no exceptions). Copy the English `work/config/grade.json`, if it has one, and apply it to the working copy; if it has none, say so.
2. Source transcript: `tools/captions/transcribe.py .. <cleaned WAV> --out-dir transcript/hi/source --language hi -- <flags, pipeline/transcribe.md>`, then `tools/captions/hindi_captions.py --romanize-only --heard transcript/hi/source/<file>.json` for a readable copy.
3. Take selection per beat (`/cut-video` rules and `pipeline/take-selection.md`: last clean take, House numbers length steps, never cut a Hindi line). English MFA and the English CTC tools don't apply: take word edges from `gpu-run vt-python tools/captions/align_mms.py` and the energy envelope, then `tools/cut/build_edl.py`, `nudge_edges.py`, `render_cut.py <K>`.
4. Captions on the cut voice: `transcribe.py ... --out-dir transcript/hi/cut --language hi`, then `tools/captions/hindi_captions.py --script ../script.md --heard transcript/hi/cut/voice.json --wav audio/voice.wav`. Read its summary; exit 2 means a word has no romanization: stop and tell me.
5. `tools/captions/build_timeline.py transcript/words_aligned.json <K> --display captions/hi-display.json` (highlights and first/last-word energy `pins` in `work/config/build_timeline.json`). `retime_onsets.py` and `fix_starts.py` correct the English aligner: don't run them.
6. Rough cut, measured length and speed-up. The handoff lists every flagged word from `captions/hi-report.json` (beat, time, kind). **Stop for my OK.**

## H2 · Map, render, deliver (`set-stage <twin> deliver`)
1. `tools/twin/setup_remotion.py projects/<name>-hi` (links the English `src/`, `scripts/`, config and `node_modules`; own `public/`). Put the Hindi `main.mp4`, `voice.wav` and `backdrop.jpg` in `work/remotion/public/`.
2. `tools/twin/map_cues.py` (cue times; read the report), then `tools/twin/trailer_ranges.py` (the Hindi 60-second cut, else the English trailer's beats).
3. Recomputed for the new footage: face track (`tools/compose/face_track.py clips/main.mp4 remotion/public/data/face.json`); jump-cut framing follows the Hindi segments; punch-ins follow the mapped cues (a composition that reads a punch map from `public/data/` gets a new one with `/add-zooms` on the Hindi emphasis words, else its audio-energy picks); SFX and mix with `tools/compose/export_sfx.sh`. A music bed reuses the English mix settings (`pipeline/sound.md`); `mix.py` doesn't add one, so if English had music, stop and tell me.
4. A Hindi beat that needs a visual change: **stop and tell me.** It is fixed in English and both render again. Never edit the linked code.
5. Checks before rendering: `npx tsc --noEmit` (in `work/remotion/`) and stills only for flagged beats (`still_frames` in `twin/map-report.json`), judged by `vision-qa`.
6. Render with `tools/jobs/render_chain.sh` in a batch; SRTs with `tools/captions/make_srt.py` (main and `--trailer-ranges audio/trailer_ranges.json`).
7. QA, same bar as English (`pipeline/qa.md`): `vt-python tools/validate/vt_validate.py projects/<name>-hi --check twin --check stage` (toolkit root), loudness and sync, caption checks, then the **fresh** `--thorough` inspect of both videos, never from cache: `gpu-run vt-python tools/inspect/video_inspect.py ../out/<main>.mp4 --thorough --language hi --captions remotion/public/data/timeline.json` (trailer: add `--caption-ranges audio/trailer_ranges.json`), judged by `vision-qa`. `tools/twin/setup_remotion.py <twin> --verify` must pass.
8. `project_state.py record-final-qa <twin> pass|fail`, then `vt_log.py record <twin> --stage deliver`. Compare costs: `vt-python tools/vt_log.py compare projects/<name> projects/<name>-hi --side-by-side`.

**Gotchas**
- Never resolve the twin's links to real paths (webpack `symlinks: false`, `--preserve-symlinks`), or the English code reads English timings.
- Remotion doesn't serve linked files in `public/`: the setup tool copies them and links only folders.
- A twin never writes into the English project.
- Write numbers in the Hindi script as spoken ("teen sau"); the tools show digits. A lone "ek" or "do" stays a word.
- Anchor a cue in the script when relative timing would miss its word; `map-report.json` shows each cue's source.
