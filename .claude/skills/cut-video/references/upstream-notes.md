# Upstream author notes and incident history

Moved from `SKILL.md` (token diet, 2026-11-20): the stories and reasoning behind the rules. The rules themselves (every threshold, padding, order and protection) stay in `SKILL.md`; this file only explains why. Text below is verbatim from the pre-trim skill, grouped by the step it came from.

## Intro

Tighten a long-form recording **aggressively**: remove silences, fillers, hedges, weak transitions, false starts, and repetitions. Preserves laughs and comedic pauses. Outputs a cleaned MP4 ready to drop into CapCut for layouts/zooms/memes.

> **This skill is more accurate than cutting from Whisper alone.** Cuts are driven by **Montreal Forced Aligner (MFA)** word boundaries (~10–20ms precision, with true inter-word silences as explicit intervals), not Whisper timestamps (±100–300ms, with pauses embedded inside word durations). Whisper is used only to produce the transcript *text* that MFA aligns to the audio. The result: tighter cuts, no clipped word onsets/tails, and reliable silence detection.

> **⚠️ But MFA times are a DRAFT, not ground truth (burned 2026-07-02, `AI is bad at jokes` DJI run).** MFA can only align the transcript whisper gave it. On retake-heavy footage whisper COLLAPSES repeated lines, so MFA smears one transcribed instance across several spoken takes — measured drift on that run was **1–6 seconds** in the back half ("the average of all working code": MFA said 217.2s, real onset 225.4s; the final "what this means" take: MFA said 114.7s, real 130.4s). Every keep boundary must be **ground-truthed with isolated-window re-transcription (Step 2.5)** before rendering. Skipping that step on that video would have produced garbage cuts for the entire second half.

## Step 1 · model choice

**Model choice (revised 2026-07-02 — "we only need the words" was WRONG):** the transcript text IS the alignment input, so transcript errors become timing errors. On the `AI is bad at jokes` run, `tiny.en` dropped exactly the words the old warning predicted ("bland", "slop"), misheard "Compare this to" as "comparative is", and collapsed full-line retakes — and MFA, aligning that wrong text, drifted 1–6s across the back half. Use **`tiny.en` only for a first fast pass to see the take structure**; if the transcript shows retakes/repetitions, or the footage is noisy/outdoor, the per-region ground-truth pass (Step 2.5) with `small.en` supplies the real cut times anyway. (A full-pass `small.en` transcript is a reasonable upgrade for the MFA input too — ~1–2 min on a 5-min video — but it ALSO collapses retakes, so it does not remove the need for Step 2.5.) For non-English use `--model base` and drop `--language`. We keep `--word_timestamps True` only so whisper times survive as a cross-check/fallback (Step 1.5 caveats, 2a-legacy) — never as the primary cut source.

## Step 1.5 · MFA install layout

**MFA is installed once, user-wide, by `/setup` — not auto-installed here** (Linux adaptation: no brew; CLAUDE.md says installs go through `/setup` with my OK). The layout `/setup` creates: Miniforge in `~/miniforge3`, a conda env `mfa` with `montreal-forced-aligner` from conda-forge, the `english_mfa` acoustic model + dictionary in `~/Documents/MFA`, and a launcher `~/bin/mfa` that runs `~/miniforge3/envs/mfa/bin/mfa "$@"`.

## Step 1.5 · caveats

- **Caveat:** MFA aligns the transcript it's GIVEN. If whisper collapsed a spoken stutter ("growth… growth marketer" → "growth marketer"), alignment drifts locally around it — keep the `silencedetect` pass (2a) as a CROSS-CHECK, and treat disagreements > 0.3s as suspect regions to re-inspect. **On retake-heavy self-shot footage the drift is not local — it's cumulative and can reach seconds** (see the warning at the top and Step 2.5). And when the noise floor kills silencedetect too (low-dynamic-range guard), you have NO automatic cross-check — Step 2.5 is then mandatory, not optional.
- **Drift smoke alarm — stretched words:** any short word whose MFA or whisper duration is ≳1s ("like" 1.16s, "there's" 1.5s, "of" 2.4s, "the" 4.9s on the 2026-07-02 run) is hiding a pause, a flub, or an ENTIRE collapsed retake inside it. Collect every stretched word up front; each one marks a region whose true content is unknown until re-windowed (Step 2.5). One stretched "the" turned out to contain a complete clean take of the whole sentence — the take that got kept.
- **Fallback:** if MFA is unavailable and I've said to go ahead without it, fall back to whisper words + audio silencedetect (2a) — and say so in the plan summary. This is the ONLY path where whisper timestamps drive cuts.

## 2a · noise-floor calibration

With MFA (Step 1.5), true silences are the TextGrid's empty-label intervals — apply the gap table below to those directly. Cross-check with audio silence detection — **but CALIBRATE the threshold to the recording's own noise floor; never hard-code `-30dB`** (added 2026-06-16, burned on a DJI-mic to-camera take whose floor sat at ~-24dB: a fixed `-30dB` saw the ENTIRE take as non-silent, so every "silent" gap measured "above threshold = content, keep" and ~8s dead-air pauses survived the cut):

## 2a · low-dynamic-range guard and no-MFA fallback

**⚠️ Low-dynamic-range guard (the real lesson, 2026-06-16):** if `S − F < ~8dB` (noisy mic — outdoor/DJI/lav with AC hum, where the per-second RMS reads the SAME during speech and silence), NO energy threshold can separate speech from silence. Do **not** trust silencedetect/volumedetect at all in that case — drive every cut from MFA word boundaries, or in the no-MFA fallback from **`small.en` word ONSETS + stretched-word pause detection** (a whisper word whose duration ≫ a normal word IS a hidden pause: keep ~`0.10 + 0.105·len(word)`s of onset, then cut to the next word's start). Say which path you used in the plan summary.

Without MFA, the silencedetect pass is the trustworthy gap source ONLY when the dynamic-range guard passes: **full-file whisper passes (turbo, `tiny.en`, and faster-whisper too) EMBED pauses inside word durations** — a 3s "word" is really "word [long pause]", inter-word *gaps* read ~0.00, and gap-based trimming does NOTHING. **Use `small.en` (not `tiny.en`) for the fallback path** — tiny stretches words across silence even worse and silently drops words ("bland", "slop") and whole retakes. Parse `silence_start`/`silence_end`, remove those intervals (keep ~0.04s pad; MFA-precision boundaries allow ~0.02s). For "almost no pauses" → `d=0.12`, pad 0.03. Combine with the dedup (2c/2d) by removing `silences ∪ dropped-word-ranges`. This is how you hit median ~1.1–1.3s.
- **Stutters whisper hides:** turbo collapses spoken repetitions ("growth… growth marketer" → "growth marketer") and varies run-to-run (drops/re-adds words). These are invisible to transcript-based cutting — MFA alignment drift + silencedetect disagreement marks the region; re-inspect it, or ask the user for the timecode and cut a precise window.

## 2d-bis · full-line retakes

Self-shot intros/promos contain **whole-sentence retakes** separated by 5–60s ("The next person is Carmen who works. … The next person, the next guest I invited is Carmen who's social and content lead at Slate") — far outside 2d's 3-second window. Detect and resolve them:
- **Detection:** fuzzy n-gram match (4-grams, similarity > 0.7) across a **60-second window**; also match sentence OPENERS (first 3–5 words) since retakes usually restart the line.
- **Keep the LAST take by default** — speakers re-record until satisfied. Exception: if the last take is incomplete/flubbed and an earlier one is clean, keep the clean one and note the override in the plan summary.
- **A retake boundary is usually preceded by a long pause, a breath, a click, or a slate-phrase** ("okay", "again", "take two") — the pause+opener-match combo is the strongest signal.
- **Surface every retake group in the Step 3 plan** (`line → takes at [t1, t2, t3] → keeping t3`) so the user can override which take survives.

## 2f · strictness pass

### 2f. STRICTNESS PASS — zero tolerance for repetitions (Louise, 2026-06-10: "get rid of ANY repetitions")
After building the keep list, run a machine scan — do NOT trust your eyes on the transcript:
1. **Scan the MFA words that fall INSIDE kept ranges** for (a) consecutive duplicate words, (b) duplicate bigrams ACROSS segment boundaries (a flubbed restart can straddle a cut — "…meet her. And we're [flub] / And we're going to…" survived a snap once), (c) duplicate sentence-openers in adjacent sentences ("So… So…" → cut the second).
2. **Cut hedge flubs** even mid-stat: "I believe", opener "Like", "I guess". Keep rhetorical repetition (parallel structure) — that's intentional.
3. **When excising a word, cut to the FULL MFA word end (+0.01s)** — a 15ms vowel residue still reads as the word.
4. **MFA OOV trap (burned 2026-06-10): acronyms/names missing from MFA's dictionary ("AI", brand names) silently VANISH from the alignment** — the word gets absorbed into its neighbor, and snapping a keep-end to "the last MFA word" then CLIPS the real spoken word. Guard: if whisper's chunk end exceeds the last MFA word end by >0.2s, trust the LATER of (whisper end, next silencedetect onset) for that boundary — and verify that junction with an isolated-segment transcription.
5. **Verification trap: whisper-of-the-output LIES twice.** It (a) COLLAPSES surviving stutters (a real "and we're… and we're" transcribes once — looks clean, isn't), and (b) HALLUCINATES context words at cut junctions (a "girls"+"Enjoy" junction transcribes as "So enjoy" — looks dirty, isn't). So verify with BOTH: the kept-range MFA dup-scan (catches real stutters), and per-segment isolated transcription of any suspect junction (clears hallucinations). Only ship when the dup-scan returns NONE.
6. **⭐ CROSS-ASR VERIFICATION — the strongest stutter detector (discovered 2026-06-10).** The MFA dup-scan only sees the words WHISPER transcribed — if whisper collapsed a phrase retake ("with the most recent video… with the most recent video" → once), MFA never knows it exists and the scan passes a dirty cut. The fix: **run the cut through a SECOND, independent ASR and diff.** **Linux/toolkit adaptation: never upload to Tella or any service.** Use a second LOCAL ASR instead: faster-whisper `large-v3` (cached) vs the `small.en` pass, or the wav2vec2 CTC aligner from `pipeline/transcribe.md` (different model → different blind spots). Upstream, a second ASR caught 5 repetitions in one pass that the whisper+MFA pipeline certified clean (a doubled phrase, a surviving "or, or", two mid-word fragments "pers-"/"per-", a doubled "into"). Workflow: run the second local ASR on the cut → scan ITS transcript for dup words/bigrams/phrases and mid-word fragments ("xyz-") → map hits back to source times → cut → re-verify. Disagreement between the two ASRs marks exactly the regions to fix or flag to the user.

## 2.5 · why ground-truth

MFA gives you the take STRUCTURE (what was said, roughly where). It does not reliably give you cut times on retake-heavy or noisy footage. Before rendering, re-transcribe **every region you plan to keep** in an isolated ±few-second window with `small.en` — within a short window whisper's word times are accurate, and it hears words the full pass dropped ("bland", "slop") and retakes the full pass collapsed ("It turns out— it turns out…").

## 2.5 · reading the windows

- **Window-edge words are stretched and untrustworthy.** A first word spanning from exactly the window start, or a last word ending at the window end, was clipped — its true onset/offset is outside the window. Re-window with the boundary moved ~1s outward before using that time.
- **Stretched words INSIDE a window hide audio too** — `small.en` collapses within-window repeats just like the full pass ("to" spanning 93.1–97.9 contained an entire abandoned take). Re-window tighter around any word ≳1s. Sometimes what's inside is a **complete clean take** that neither full-pass ASR surfaced — check before assembling a splice from fragments.
- **Two windows can disagree about the same words** (one caught a flub the other clipped). Resolve with a third window positioned so the disputed moment sits mid-window, away from both edges.
- Final keep times: pad onset −0.03s, offset +0.04–0.08s (tight — stacked +0.10 pads across 20 keeps add 2s of mush).
- **Trim pauses INSIDE kept takes too (added 2026-07-02 — "even less silences").** Removing retakes and inter-take gaps is not enough: fluent takes still carry mid-sentence beats ("…for a living, [0.3s] I want to know…") and they add up. Scan the ground-truth words within each keep for inter-word gaps > 0.2s and trim each to ~0.1s (cut `[gap_start+0.05, gap_end−0.05]`). Leave deliberate rhetorical beats ("median… or average") no shorter than ~0.15s.
- **Stretched-word trap, keep-side (burned 2026-07-02):** a drawn-out spoken word looks identical to word+trailing-pause in the ASR ("slooop" transcribed as `slop 285.08–286.32`). Trimming what looks like the pause half CLIPS THE WORD mid-vowel. Before trimming into any stretched word at a keep boundary, re-window it tightly to find where the voice actually stops — and if the post-render verify transcript is missing a word that was there before, your trim ate it: push the boundary back out.

Cost on a 5-min video: ~10–15 windows × a few seconds of `small.en` each ≈ 2 minutes. It is the difference between a clean cut and re-doing the whole back half.

## 3 · render-first history

**Render the plan without waiting — but in this toolkit the result is the ROUGH CUT, and CLAUDE.md's checkpoint still applies: stop after rendering it and wait for my OK before composing.** Print the summary and start the render in the same turn (changed 2026-07-09: the approval gate cost Louise a wasted wait when she didn't notice the question; the render is non-destructive and cheap to redo, so render-first is strictly better). Print this summary, then go straight to Step 4:

## 3 · self-check exceptions

- **Exception — retake-heavy footage (2026-07-02):** when most of the runtime is abandoned takes, the compression comes from dropping whole lines, not word-level slicing — median keep lands at 3–5s and compression at 65–75%, and that's CORRECT. Judge by compression % and final-script cleanliness instead; do NOT force extra mid-sentence cuts into fluent kept takes just to hit the 1.1–1.5s median (that target is for filler-dense monologue where nothing is re-recorded).

Run the self-check yourself and fix violations before rendering — that's the quality gate now, not the user. Then render immediately. The user reviews the *result*; if a cut killed a laugh or an intentional pause, adjust the keep list and re-render (fast — trim/concat, not re-transcription).

## Pitfalls

- **Don't wait for approval before rendering the rough cut** (changed 2026-07-09 — the gate wasted more time than it saved), but do stop at the rough cut checkpoint afterwards. Print the plan, render immediately. The old worry (a "silent" gap holding a laugh, a "filler" that's intentional emphasis) is handled by the amplitude check below + preserved-pauses list in the summary — and a bad cut just means a quick re-render.
- **Don't trim a long "silence" without checking amplitude** — that's usually laughter, a thinking pause, or a setup-payoff beat.
- **Never transcribe source/proxy audio.** `audio.wav` is derived only from the Prep-verified cleaned WAV in Step 0.75; all later ASR windows come from that cleaned track. Final cut audio is trimmed from the verified cleaned 48 kHz WAV, not the proxy.
- **Don't re-encode audio twice.** If you only changed video, use `-c:a copy` to skip an unnecessary AAC pass.
- **Don't be timid.** Default to `aggressive`. The reference cut style is fast — if the output feels "safe", it's not matching Louise's CapCut pacing.
- **Don't render from MFA times alone on retake-heavy or noisy footage.** Measured 1–6s drift on the 2026-07-02 DJI run. Ground-truth every keep boundary with isolated windows (Step 2.5) first.
- **Don't scale a portrait source to 1920:1080.** Probe orientation first; DJI/phone footage is usually 9:16.
- **Don't trust window-edge word times** from an isolated transcription — a word touching the window boundary is clipped/stretched; re-window before using it as a cut point.
