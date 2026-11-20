---
name: cut-video
description: Tighten a long recording aggressively — remove silences, fillers, hedges, false starts, and repetitions while preserving laughs and comedic pauses. Cuts are driven by Montreal Forced Aligner (MFA) word boundaries (auto-installs on first run), not raw Whisper timestamps. Use when the user pastes a video and says "cut this", "tighten this video", "remove silences", "strip ums", "clean this up", or any variant of "make this video shorter without losing the good parts".
---

# Cut Video

## Linux adaptation (video-toolkit)

Changed from upstream for this machine; these notes win over anything below.

- **Platform:** Ubuntu 24.04, NVIDIA GPU. `apt` instead of `brew`; `xdg-open` instead of `open`; `-hwaccel cuda` instead of `videotoolbox`; `h264_nvenc` instead of `libx264`/`h264_videotoolbox`. Never fall back to the CPU silently (`pipeline/gpu.md`).
- **Whisper:** `gpu-run whisper-ctranslate2 --device cuda --compute_type float16` (faster-whisper, same flags and JSON shape as openai-whisper) instead of `whisper`/`mlx_whisper`. Models are cached in `~/.cache`.
- **Python:** `vt-python` (the shared user venv with numpy, Pillow, faster-whisper) instead of `python3`.
- **Paths:** work in `projects/<name>/work/<skill>/`, never `/tmp` or next to the source. `raw/` and `assets/` are read-only.
- **Priority:** `CLAUDE.md` and `brand.md` win over this skill's defaults (colors, fonts, caption style, pacing, motion).
- **MFA:** installed once by `/setup` (Miniforge + conda env `mfa`, launcher `~/bin/mfa`). This skill no longer auto-installs it. MFA runs on the CPU by design.
- **Never upload** the cut to Tella or any service. Cross-check with a second local ASR.
- **Pacing:** keep-last-take matches CLAUDE.md, but the pause lengths in `pipeline/take-selection.md` (and `/reel`'s tighter ones) override this skill's `aggressive` gap table. Use `balanced` for tutorials unless I ask for aggressive.
- **Checkpoint:** render the cut, then stop at the rough cut and wait for my OK (CLAUDE.md). The "don't wait for approval" advice below only means don't ask before rendering it.

Tighten a long-form recording **aggressively**: remove silences, fillers, hedges, weak transitions, false starts, and repetitions; preserve laughs and comedic pauses. Cuts are driven by **MFA** word boundaries (~10–20 ms, true silences as empty intervals); Whisper only supplies the transcript *text*. **MFA times are a draft, not ground truth:** on retake-heavy footage Whisper collapses repeated lines and MFA drifts 1–6 s, so every keep boundary is ground-truthed in Step 2.5 before rendering.

**Style target** (`aggressive`): ~1 cut every 1.3–1.5 s (median ~1.1 s), ~40–60% runtime reduction, cuts mid-sentence too, word-by-word tightening of fillers, hedges and weak openers.

References (load only when needed): `references/upstream-notes.md` (the incidents and reasoning behind each rule) · `references/benchmark.md` (the calibration video) · `references/manual-editor.md` (Step 3.5, only when I ask for the editor) · `references/2a-legacy.md` (gap-table history).

## Inputs

- Video file path (the user will provide; otherwise ask)
- Optional: tone preference (`aggressive` / `balanced` / `sentimental` / `documentary`) — default: `aggressive`

## Working directory

`projects/<name>/work/cut-video/` — mkdir at start, leave artifacts for debugging.

---

## Step 0 — Inspect source and pass the voice-cleaning gate

If the Prep handoff in `log.md` already maps this recording to a cleaned WAV whose gate passed, use that WAV (`projects/<name>/work/audio/cleaned/<recording-id>.wav`) and skip to the next step. Otherwise (standalone use) run the gate in `pipeline/voice-cleaning.md`: run `vt-python tools/voice_preflight.py` (stop on `NOT READY`), probe the original, assign each talking-head recording an ID, run `vt-python tools/clean_audio.py "$SRC" "projects/<name>/work/audio/cleaned/<recording-id>.wav" --preset studio --mode quality --report "projects/<name>/work/audio/reports/<recording-id>-clean-report.json"` once per recording, check every report (`status: succeeded`, matching `run_id`, `stages.wpe` and `stages.deepfilternet3` both `processed`, `production_gate.automated_checks_passed: true`), and listen to each original/cleaned pair at matched loudness unless the approved-setup exemption in `pipeline/voice-cleaning.md` applies. A non-zero exit or any failed check: stop and report. If listening is unavailable, disclose it and request explicit approval before Whisper. Never switch modes, transcribe source audio, or overwrite another recording's output/report without explicit approval. Continue only after every relevant recording passes.

## Step 0.5 — Make a video-only proxy

If the source is HEVC, >500MB, or 4K+, transcode to a 1080p H.264 video-only working copy. Video-frame steps may use the proxy; audio analysis and rendering use the verified cleaned WAV.

**Check orientation first** (`ffprobe … width,height`): phone/DJI footage is often 9:16. `scale=1920:1080` only for landscape; `scale=1080:1920` for portrait (or the orientation-proof `scale=-2:1080` / `scale=1080:-2`).

```bash
ffmpeg -y -hwaccel cuda -i "$SRC" \
  -vf scale=1920:1080 \        # portrait sources: scale=1080:1920
  -c:v h264_nvenc -preset p5 -rc vbr -cq 20 -b:v 0 -pix_fmt yuv420p \
  -an \
  projects/<name>/work/cut-video/proxy.mp4
```

- `-hwaccel cuda` on the INPUT (NVDEC decodes HEVC; without it, minutes instead of seconds).
- `h264_nvenc` on the GPU (never the CPU silently). Faster throwaway proxy: `-preset p1`.

## Step 0.75 — Prepare ASR audio from the verified cleaned recording

Use only the WAV that passed Step 0's report and listening checks. Never proxy audio, source video audio, or an unverified extraction for Whisper or MFA.

```bash
ffmpeg -y -i projects/<name>/work/audio/cleaned/<recording-id>.wav \
  -ac 1 -ar 16000 projects/<name>/work/cut-video/audio.wav
```

## Step 1 — Get the transcript TEXT (whisper, as input for MFA)

MFA is a forced aligner, not a transcriber. Whisper's only job is the text; **whisper word timestamps are NOT used for cutting** (±100–300 ms, pauses embedded in word durations).

```bash
gpu-run whisper-ctranslate2 --device cuda --compute_type float16 projects/<name>/work/cut-video/audio.wav \
  --model tiny.en --word_timestamps True --output_format json \
  --output_dir projects/<name>/work/cut-video --language en
```

**Model choice:** transcript errors become timing errors. Use **`tiny.en` only for a first fast pass to see the take structure**; with retakes/repetitions or noisy/outdoor footage, Step 2.5 with `small.en` supplies the real cut times. A full-pass `small.en` is a reasonable upgrade for the MFA input (~1–2 min on a 5-min video) but also collapses retakes, so Step 2.5 is still needed. Non-English: `--model base`, drop `--language`. `--word_timestamps True` stays only as a cross-check/fallback, never the primary cut source.

## Step 1.5 — Align the transcript to the audio with MFA — the timing engine

**All cut decisions (gaps, fillers, false starts, retakes) use MFA word times.** Layout from `/setup`: Miniforge `~/miniforge3`, conda env `mfa`, `english_mfa` acoustic model + dictionary in `~/Documents/MFA`, launcher `~/bin/mfa`.

Check at the start of every run:

```bash
command -v mfa && mfa version \
  && mfa model inspect acoustic english_mfa >/dev/null 2>&1 \
  && mfa model inspect dictionary english_mfa >/dev/null 2>&1 \
  && echo MFA-ready
```

If that fails, stop and tell me MFA is missing and that `/setup` installs it. Only use the whisper+silencedetect fallback if I say so, and say so in the plan summary. MFA on the CPU (Kaldi) is expected, not a GPU fallback.

**Per run:**
```bash
# corpus = a dir with audio.wav + audio.txt (the whisper transcript as PLAIN TEXT, no timestamps)
mkdir -p projects/<name>/work/cut-video/corpus
cp projects/<name>/work/cut-video/audio.wav projects/<name>/work/cut-video/corpus/
vt-python -c "import json;d=json.load(open('projects/<name>/work/cut-video/audio.json'));open('projects/<name>/work/cut-video/corpus/audio.txt','w').write(d['text'])"
mfa align --clean projects/<name>/work/cut-video/corpus english_mfa english_mfa projects/<name>/work/cut-video/aligned
# → aligned/audio.TextGrid — "words" tier: (start, end, word); EMPTY-label intervals = true silences
```
Parse the TextGrid `words` tier (`praatio` or a 20-line parser). True word boundaries → cut pads shrink to ~0.02 s; true silences are explicit empty intervals, so the 2a gap table works directly off the TextGrid.
- **Caveat:** MFA aligns the transcript it's given. Where whisper collapsed a stutter, alignment drifts: keep `silencedetect` (2a) as a CROSS-CHECK and treat disagreements > 0.3 s as suspect regions to re-inspect. On retake-heavy self-shot footage the drift is cumulative (seconds). When the noise floor also defeats silencedetect (low-dynamic-range guard), there is no automatic cross-check: Step 2.5 is mandatory.
- **Drift smoke alarm — stretched words:** any short word whose MFA or whisper duration is ≳1 s hides a pause, a flub, or an entire collapsed retake (sometimes a complete clean take). Collect every stretched word up front; each marks a region to re-window in Step 2.5.
- **Fallback:** if MFA is unavailable and I've said to go ahead, use whisper words + audio silencedetect (2a) and say so in the plan summary. This is the ONLY path where whisper timestamps drive cuts.

## Step 2 — Build the cut list (AGGRESSIVE by default)

Compute (start, end) intervals to KEEP from the **MFA word intervals** (whisper JSON only as fallback).

### 2a. Silence gaps — MFA empty intervals first, audio silencedetect as cross-check
Apply the gap table to the TextGrid's empty-label intervals. Cross-check with audio silence detection, **calibrated to the recording's own noise floor; never hard-code `-30dB`** (a floor at ~-24 dB makes every gap read as content, and dead air survives):

```bash
# 1. Measure the noise floor F and speech level S from per-0.5s-window RMS
#    (slice the wav into 0.5s windows, run volumedetect on each, collect mean_volume;
#     F ≈ 10th-percentile window RMS  (room tone),  S ≈ 90th-percentile  (speech))
# 2. Set the silence threshold RELATIVE to the floor, not absolute:
THRESH=$(vt-python -c "print(f'{F + 6:.0f}')")        # 6 dB above the measured floor
ffmpeg -i audio.wav -af silencedetect=noise=${THRESH}dB:d=0.14 -f null - 2>&1 | grep silence_
```

**Low-dynamic-range guard:** if `S − F < ~8dB` (noisy mic: outdoor/DJI/lav with hum), no energy threshold separates speech from silence. Don't trust silencedetect/volumedetect at all: drive every cut from MFA word boundaries, or in the no-MFA fallback from **`small.en` word ONSETS + stretched-word pause detection** (keep ~`0.10 + 0.105·len(word)` s of onset, then cut to the next word's start). Say which path you used in the plan summary.

**No-MFA fallback:** silencedetect is the trustworthy gap source ONLY when the guard passes (full-file whisper embeds pauses inside word durations, so gap-based trimming does nothing). Use **`small.en`, not `tiny.en`**, for this path. Parse `silence_start`/`silence_end`, remove those intervals (pad ~0.04 s; MFA-precision boundaries allow ~0.02 s). "Almost no pauses" → `d=0.12`, pad 0.03. Combine with 2c/2d by removing `silences ∪ dropped-word-ranges`.
- **Stutters whisper hides** (collapsed repetitions, run-to-run variation) are invisible to transcript-based cutting: MFA drift + silencedetect disagreement marks the region; re-inspect it, or ask the user for the timecode and cut a precise window.

**Gap table** (still live; in this toolkit `pipeline/take-selection.md` / `/reel` pause lengths override it):

| Gap | `aggressive` (default) | `balanced` | `sentimental` | `documentary` |
|---|---|---|---|---|
| `< 0.25s` | keep | keep | keep | keep |
| `0.25–1s` | trim to **0.1s** | trim to 0.3s | trim to 0.5s | keep |
| `1–3s` | trim to **0.2s** | trim to 0.8s | trim to 1.5s | trim to 2s |
| `> 3s` | trim to **0.2s** | trim to 0.5s | trim to 1s | trim to 3s |

### 2b. Filler words — cut with 50ms padding

Always cut: `um`, `uh`, `umm`, `uhh`, `er`, `erm`, `ah`, `mhm`, `hmm` (standalone)

### 2c. Hedges & weak transitions — cut aggressively in default mode

Cut these when delivered as filler (not substantive content). Mark for cut, then verify against context in the review step:

- **Hedges:** `like` (as filler, not as comparison), `you know`, `I mean`, `I guess`, `I think` (when hedging, not asserting), `kind of`, `sort of`, `basically`, `literally`, `actually` (as filler)
- **Weak transitions:** `so` (sentence-opener), `and so`, `and then`, `but um`, `but uh`, `okay so`, `right so`, `well`
- **Redundant qualifiers:** `kind of like`, `sort of like`, `or whatever`, `or something`
- **Re-orientation phrases:** `anyway`, `so anyway`, `the thing is`, `what I'm saying is`, `to be honest`, `honestly`

In `balanced` / `sentimental` / `documentary` modes, only cut hedges that precede a re-statement (false start, see 2d). Keep them in conversational moments.

### 2d. False starts and repetitions — cut aggressively

- **Self-corrections:** the same opening re-stated within ~3 s (`"I want — I wanted to..."`). Drop the earlier attempt + the gap.
- **Restart preambles:** `"so basically what I'm saying is..."`, `"the point is..."`, `"let me start over..."`. Drop the preamble, keep the point.
- **Verbatim repetitions:** same 3+ words twice in a row. Keep the cleaner take.

Implementation: sliding-window fuzzy match on consecutive word n-grams; 3-gram similarity > 0.8 within a 3-second window → flag the earlier instance for removal.

### 2d-bis. FULL-LINE RETAKES (self-shot to-camera recordings)
Whole-sentence retakes 5–60 s apart, outside 2d's window:
- **Detection:** fuzzy n-gram match (4-grams, similarity > 0.7) across a **60-second window**; also match sentence OPENERS (first 3–5 words).
- **Keep the LAST take by default.** Exception: if the last take is incomplete/flubbed and an earlier one is clean, keep the clean one and note the override in the plan summary.
- **Boundary signal:** a long pause, breath, click or slate-phrase ("okay", "again", "take two") before a matching opener.
- **Surface every retake group in the Step 3 plan** (`line → takes at [t1, t2, t3] → keeping t3`).

### 2e. NEVER cut these — protect explicitly

- **Laughs.** Whisper transcribes laughter as silence. Before applying ANY silence cut, check the window's amplitude (`ffmpeg -i audio.wav -af "volumedetect" -f null - 2>&1 | grep mean_volume`; per-window: `-af "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level"`) against the **measured noise floor F** (2a), never a fixed dB: window RMS > `F + ~10dB` = audible content (laugh, breath, reaction) → keep. When `S − F < ~8dB`, RMS can't tell a laugh from room tone: fall back to MFA/word-onset timing and surface anything ambiguous in the plan.
- **Comedic beats.** A deliberate pause after a punchline. In `aggressive` mode, still trim to 0.4–0.6s (don't kill it, just tighten).
- **Reaction sounds.** Sighs, "ooh", "wow", gasps — all content.
- **Single-word punchlines.** If a sentence ends with a one-word zinger after a beat, keep the beat.

### 2f. STRICTNESS PASS — zero tolerance for repetitions
After building the keep list, run a machine scan; don't trust your eyes on the transcript:
1. **Scan the MFA words INSIDE kept ranges** for (a) consecutive duplicate words, (b) duplicate bigrams ACROSS segment boundaries (a flubbed restart can straddle a cut), (c) duplicate sentence-openers in adjacent sentences ("So… So…" → cut the second).
2. **Cut hedge flubs** even mid-stat: "I believe", opener "Like", "I guess". Keep rhetorical repetition (parallel structure).
3. **When excising a word, cut to the FULL MFA word end (+0.01s)**; a 15 ms vowel residue still reads as the word.
4. **MFA OOV trap:** acronyms/names missing from MFA's dictionary ("AI", brands) vanish from the alignment and snapping a keep-end to "the last MFA word" clips the real word. Guard: if whisper's chunk end exceeds the last MFA word end by >0.2 s, trust the LATER of (whisper end, next silencedetect onset) for that boundary, and verify that junction with an isolated-segment transcription.
5. **Whisper-of-the-output lies twice:** it collapses surviving stutters and hallucinates words at cut junctions. Verify with BOTH the kept-range MFA dup-scan and per-segment isolated transcription of any suspect junction. Only ship when the dup-scan returns NONE.
6. **⭐ Cross-ASR verification (strongest stutter detector).** Run the cut through a SECOND, independent **local** ASR (never upload): faster-whisper `large-v3` (cached) vs the `small.en` pass, or the wav2vec2 CTC aligner from `pipeline/transcribe.md`. Scan its transcript for dup words/bigrams/phrases and mid-word fragments ("xyz-") → map hits back to source times → cut → re-verify. Disagreement between the two ASRs marks the regions to fix or flag.

## Step 2.5 — GROUND-TRUTH every keep boundary with isolated windows

Before rendering, re-transcribe **every region you plan to keep** in an isolated ±few-second window with `small.en` (short-window word times are accurate, and it hears dropped words and collapsed retakes).

```bash
# windows: name:start:duration — start ≥0.5s BEFORE the expected onset
for n in "r1:5.5:8.4" "r2:17.0:6.0" "r3:30.5:6.0"; do
  f=${n%%:*}; rest=${n#*:}; o=${rest%%:*}; t=${rest##*:}
  ffmpeg -y -hide_banner -loglevel error -ss $o -t $t -i audio.wav gt/$f.wav
  gpu-run whisper-ctranslate2 --device cuda --compute_type float16 gt/$f.wav --model small.en --word_timestamps True --output_format json --output_dir gt --language en >/dev/null 2>&1
  vt-python -c "
import json
d=json.load(open('gt/$f.json'))
print('=== $f (+$o) ===')
for s in d['segments']:
    for w in s.get('words',[]):
        print(f\"{$o+w['start']:7.2f}-{$o+w['end']:7.2f} {w['word']}\")"
done
```
(zsh-safe loop: don't use `set -- $var`.)

Rules for reading the windows:
- **Window-edge words are untrustworthy:** a first word starting exactly at the window start, or a last word ending at the window end, was clipped. Re-window with the boundary moved ~1 s outward before using that time.
- **Stretched words inside a window hide audio too:** re-window tighter around any word ≳1 s. What's inside may be a complete clean take; check before splicing from fragments.
- **Two windows disagree** about the same words → resolve with a third window placing the disputed moment mid-window.
- **Final keep times:** pad onset −0.03 s, offset +0.04–0.08 s (stacked +0.10 pads add mush).
- **Trim pauses INSIDE kept takes too:** inter-word gaps > 0.2 s in the ground-truth words → trim each to ~0.1 s (cut `[gap_start+0.05, gap_end−0.05]`). Leave deliberate rhetorical beats no shorter than ~0.15 s.
- **Stretched-word trap, keep-side:** a drawn-out word looks like word+pause. Before trimming into a stretched word at a keep boundary, re-window tightly to find where the voice stops; if the post-render verify transcript lost a word, the trim ate it: push the boundary back out.

Cost on a 5-min video: ~10–15 windows ≈ 2 minutes.

## Step 3 — Show the plan, render immediately

**Render without waiting, but the result is the ROUGH CUT: stop after rendering it and wait for my OK before composing (CLAUDE.md).** Print this summary, then go straight to Step 4:

```
Original duration: 7m 25s
Cleaned duration: 3m 58s
Cut: 3m 27s (47%)
Total keep intervals: 312
Median cut duration: 1.2s (target: 1.1–1.5s)
Hard cuts (dead air > 3s removed): 23
Filler hits: 47
Hedge/transition cuts: 89
False-start drops: 12
Notable preserved long pauses: list timestamps + context (laughs, punchlines)
```

**Self-check vs benchmark** (run it yourself and fix violations before rendering):
- Median cut > 2 s → not aggressive enough: tighten gap thresholds or expand the hedge list, retry.
- Median cut < 0.7 s → over-cut (killing breath/cadence): loosen the 0.25–1 s threshold to 0.3 s.
- Target compression: 40–60% in aggressive mode.
- **Exception — retake-heavy footage:** median keep 3–5 s and compression 65–75% is CORRECT. Judge by compression % and final-script cleanliness; don't force mid-sentence cuts into fluent kept takes to hit the 1.1–1.5 s median.

If a cut killed a laugh or an intentional pause, adjust the keep list and re-render (trim/concat, not re-transcription). Manual timeline editor: only when I ask (`references/manual-editor.md`).

## Step 4 — Render with `trim` + `concat`, NOT `select`

`select`/`aselect` compresses video frames but not audio PTS, so A/V drift. One trim+atrim pair per keep interval, then concat:

```
[0:v]trim=A1:B1,setpts=PTS-STARTPTS[v0];
[1:a]atrim=A1:B1,asetpts=PTS-STARTPTS[a0];
[0:v]trim=A2:B2,setpts=PTS-STARTPTS[v1];
[1:a]atrim=A2:B2,asetpts=PTS-STARTPTS[a1];
...
[v0][a0][v1][a1]...concat=n=N:v=1:a=1[outv][outa]
```

Write the filtergraph to a file and use `-filter_complex_script`:

```bash
ffmpeg -y -hwaccel cuda -i projects/<name>/work/cut-video/proxy.mp4 \
  -i projects/<name>/work/audio/cleaned/<recording-id>.wav \
  -filter_complex_script projects/<name>/work/cut-video/filter.txt \
  -map "[outv]" -map "[outa]" \
  -c:v h264_nvenc -preset p5 -rc vbr -cq 20 -b:v 0 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  projects/<name>/work/cut-video/cleaned.mp4
```

**More than ~500 trims:** per-segment extract + lossless concat instead (no re-encode on the trim pass):
1. Extract video-only keep intervals from `proxy.mp4` and audio keep intervals from the verified cleaned 48 kHz WAV; never copy proxy/source audio.
2. Build separate concat demuxer files and concatenate video and cleaned audio independently.
3. Mux the concatenated streams and verify start/middle/end sync.

## Step 5 — Deliver

- Save to `projects/<name>/work/cut-video/cleaned.mp4` (never next to the source). The 720p rough cut preview goes to `out/roughcut_preview.mp4` per `pipeline/take-selection.md`.
- Print one line: original duration → cleaned duration, percent cut, median cut, output path.
- `xdg-open` the file so the user can review immediately.
- Revisions are cheap (proxy + ground-truthed times stay in the working dir). If the Step 3.5 editor was used, remind the user it's still live for pasting decisions back.
- Offer to iterate: re-tune gap thresholds, switch tone preset, mark moments to preserve/cut.

---

## Pitfalls

- **Don't skip `-hwaccel cuda`** on the proxy step (5+ min vs ~30 s on 4K HEVC).
- **Don't use `select` for cuts**; use trim+concat.
- **Don't encode on the CPU.** `h264_nvenc`; if it fails, fix it or stop and tell me.
- **Don't wait for approval before rendering the rough cut**, but do stop at the rough-cut checkpoint afterwards. Bad cuts are a quick re-render; the amplitude check + preserved-pauses list cover laughs and intentional emphasis.
- **Don't trim a long "silence" without checking amplitude** (laughter, thinking pause, setup-payoff beat).
- **Never transcribe source/proxy audio.** `audio.wav` comes only from the Prep-verified cleaned WAV (Step 0.75); all ASR windows come from that track; final cut audio is trimmed from the verified cleaned 48 kHz WAV.
- **Don't re-encode audio twice.** Video-only change → `-c:a copy`.
- **Don't be timid.** Default to `aggressive`; if the output feels "safe", it's not matching the pacing.
- **Don't render from MFA times alone on retake-heavy or noisy footage**: Step 2.5 first.
- **Don't scale a portrait source to 1920:1080.** Probe orientation first.
- **Don't trust window-edge word times** from an isolated transcription; re-window first.
- **The cleaned cut is a working file, not the delivery.** Final render and loudness: `pipeline/render.md`.

## What this skill explicitly does NOT do

- Zooms, layouts, motion graphics (`/add-zooms`, the Remotion composition)
- Memes or b-roll (see `/clipify` for short-form cuts)
- Burn captions (separate pass after cleanup)
- Upload anywhere

Keep this skill focused on one thing: produce a tighter MP4 from a long-form recording, fast and aggressive.
