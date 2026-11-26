# Subtitles

**Goal:** SRT files that match the final edit exactly, delivered next to each MP4.

**Tools** (run from `work/`; paths relative to the toolkit root)
- `vt-python tools/captions/build_timeline.py transcript/words_ctc_fixed.json <K> --config config/build_timeline.json`: script tokens on spoken times. All episode settings (`fix`, `pins`, `time_fix`, `highlights`, `display`, `word_fix` with literal `~`) live in the config.
- `vt-python tools/captions/make_srt.py --out ../out/<name>_9x16.srt --trailer-ranges audio/trailer_ranges.json --trailer-out ../out/<name>_trailer_9x16.srt`.

**Do**
- Generate the SRT from the final timeline's words (output times), never from the raw transcript.
- Write one SRT per edit: `out/<name>.srt` and `out/<name>_trailer_9x16.srt`, plus `out/<name>_trailer_16x9.srt` for long-form (> 3:00) only.
- Cues: at most 2 lines, about 42 characters per line, 1–6 s long. Break at punctuation or phrase boundaries, never between an article and its noun.
- Use my actual spoken words, but with correct spelling and casing for tech terms (e.g. pgvector, tRPC, PostgreSQL, GraphQL, Supabase, Turborepo). Keep a glossary in `script.md` and apply it to both the burned-in captions and the SRT.
- Caption the opener as "Namoshkar!", spelled exactly like that (Whisper may write "Namaskar" or "Namaste"); the closer as "Bye bye, sayonara!".
- Where an edit replaced a misspoken word by agreement, the SRT shows the agreed word, the same as the burned-in caption.
- Leave no cues during the typing intro or the end card.

**Checks**
- Cue count is sensible. No overlaps, no negative durations.
- Spot-check three cues against the video at the start, middle and end. Each must land within 1 frame of the word.
- The SRT's last cue ends before the video ends.
- Whisper with `--condition_on_previous_text False` can return a long stretch with no punctuation or capitals (`ag-ui`, 0:26–1:35). Captions then page badly and the SRT splits mid-sentence. Add the punctuation to the caption words (a phrase → mark list in the caption text, then capitalise after `.?!`) instead of patching cues; capitalising every cue made it worse.
- Glossary terms that must stay lower-case (`docker build`) get capitalised by `word_fix` ("docker" → "Docker"): mark them literal in `display` with a `~` prefix (stripped at output). Highlight words that recur light up everywhere unless scoped: put the target in brackets inside a phrase (`'an [image] is'`).
- Script-driven captions (`docker-is-dead`; now `tools/captions/build_timeline.py`): difflib-align the script tokens to the CTC-timed spoken words; equal/replace blocks take the spoken times and show the script token (spelling, casing, punctuation and agreed misspeak fixes come free), script-only words are interpolated, spoken-only words are dropped unless whitelisted (real extras like "the real reason"). Replaced ~60 hand-written FIX/PUNCT/CAP rules and also dropped Whisper's invented repeats. Print the replace/drop report and read it.
- A caption token that keeps its own `!` ("Namoshkar!", "sayonara!") plus the stored punctuation field printed "Namoshkar!!" in the SRT (`system-design-of-ai/05`). Strip the token's trailing `!` before appending the punctuation, and grep every SRT for `!!`, `..` and `,,`. Also split a cue after a comma once it passes ~40 characters: an 84-char cap left 45–52-char lines and a line ending on "the".
- CTC-aligned words can be only ~2 frames long, so a "gap > 18 frames → new cue" rule splits mid-phrase ("Both / cost 25¢", "Next / in AI System Design", `04-cost-metering`). Split on a gap only when the previous word ends in punctuation or the cue already has ≥ 24 characters (`make_srt.py`).
- The `≥ 24 characters` gap split still broke "…rediscovering code your / team already wrote." (a 0.6 s pause after "your"), and a sentence shorter than the 20-character flush ("team already wrote.") then ran into the next sentence in one cue (`Graphify`). Never split on a gap right after an article, possessive or preposition (a, an, the, your, to, of, in, with, and), and close a cue at `.?!` once it has > 8 characters.
- Caption display rules (`DISP`) for short tokens must carry context: a rule `U-P → UP` also turned "adds up to 35%" into "adds UP to" (`sdai-12`). Match the phrase ("U-P and Bihar"), never the bare token.
