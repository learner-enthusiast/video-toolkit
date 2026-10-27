# Subtitles

**Goal:** SRT files that match the final edit exactly, delivered next to each MP4.

**Do**
- Generate the SRT from the final timeline's words (output times), never from the raw transcript.
- Write one SRT per edit: `out/<name>.srt`, `out/<name>_trailer_16x9.srt`, `out/<name>_trailer_9x16.srt`.
- Cues: at most 2 lines, about 42 characters per line, 1–6 s long. Break at punctuation or phrase boundaries, never between an article and its noun.
- Use my actual spoken words, but with correct spelling and casing for tech terms (e.g. pgvector, tRPC, PostgreSQL, GraphQL, Supabase, Turborepo). Keep a glossary in `script.md` and apply it to both the burned-in captions and the SRT.
- Where an edit replaced a misspoken word by agreement, the SRT shows the agreed word, the same as the burned-in caption.
- Leave no cues during the typing intro or the end card.

**Checks**
- Cue count is sensible. No overlaps, no negative durations.
- Spot-check three cues against the video at the start, middle and end. Each must land within 1 frame of the word.
- The SRT's last cue ends before the video ends.
