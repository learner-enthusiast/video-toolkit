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

**Gotchas**
- Unpunctuated Whisper stretches break cues: add the punctuation to the caption words and capitalise after `.?!`; never patch cues.
- Lower-case terms: `word_fix` capitalises, a `~` prefix in `display` stays literal. Scope recurring highlights as `'an [image] is'`.
- Captions show script tokens on spoken times (`tools/captions/build_timeline.py`): read its replace/drop report.
- Grep every SRT for `!!`, `..` and `,,`.
- Split an SRT cue on a pause only after punctuation or ≥ 24 characters: CTC words are short and leave fake gaps.
- Never split a cue after an article, possessive or preposition; close it at `.?!` once past 8 characters.
- `display` rules match a phrase with context ("U-P and Bihar"), never a bare short token.
