# Music

**Goal:** a very faint instrumental bed under my voice in every video and its Hindi twin. **I choose the music; Claude never picks, rates or describes it.** Tools measure and enforce. My voice is never lowered, compressed differently or re-leveled for music: only the music moves. Values: `CLAUDE.md` → House numbers (gap, fail level, fade-in, pause hold) and `config/music.json`.

Tool paths are relative to the toolkit root.

## Library
- `music/index.md` (tracked, one row per track; look up with `grep`), `music/licenses/` (tracked proof per track), `music/tracks/` (gitignored audio).
- **Add:** `vt-python tools/music/add_track.py <file> --source-url … --license-type "…" --license-file … --mood "calm,tech" --instrumental [--house] [--credit "exact line"]`. It refuses without a license file or `--instrumental` (`--allow-vocals` exists, never the default, never ★house). It measures length, BPM, LUFS, true peak and a loop seam (a bar boundary, else "no"), copies both files and writes the row with the sha256.
- **New machine:** `vt-python tools/music/restore.py` lists missing or changed tracks with their `source_url`.

## Licensing
- A track enters only with proof of a license covering **all** my platforms: YouTube incl. Shorts, Instagram, Facebook, LinkedIn, X, Threads.
- OK: Uppbeat (a plan covering these), YouTube Audio Library **via its own download button** (check each track's terms for use outside YouTube), any source with an explicit license file. Pixabay is allowed and gets `content_id_risk: known risk`.
- **Never** rips from YouTube, Spotify or similar; **never `yt-dlp` for music** (it's only for downloading my own uploads, e.g. for `/clipify`). The add tool refuses those URLs, but it can't check a license: that's on the file I give it.

## Choosing (end of Cut)
`vt-python tools/music/pick.py <project> --prompt <prompt.md>` (or `--value "<line>"`, empty when the prompt has none) records `project-state.json` `music` and a `**Music bed:**` log line.

| `**Music:**` line | Result |
|---|---|
| an id or file | that track |
| `none` | no bed |
| no line | rotation: the least recently used ★house track that fits or loops; ties by id |
| `audition` or `audition [a,b,c]` | audition; with no ids, the 3 least recently used ★house tracks |

No ★house track that fits → no bed; **say so in the Cut handoff**. A Hindi twin inherits the English track (its own line is ignored). Trailers use the main video's track.

## Audition
`gpu-run vt-python tools/music/audition.py <project> [--tracks a b]`, a heavy job. It refuses before the cleaned recording, `work/audio/voice.wav` and the cut's word timings exist (`--words` for another file). Per track it builds the real bed, cuts the busiest 20 s and the longest pause (else the hook), and runs the gap and clarity checks. Passing tracks get `out/music-audition/<NN>-<id>/{voice_only,with_music,with_music_phone}.wav` (phone: mono, band-limited); failing ones are listed as rejected in `report.md`.
- List the report lines and preview paths in the Cut handoff and the rough-cut stop message. My reply ("cut ok, music 2") → `vt-python tools/project_state.py set-music <project> 2` (also an id or `none`), then record the rough-cut approval.

## Mix (Compose, every deliverable)
`tools/compose/export_sfx.sh` runs it: `mix.py` (voice stem + SFX) → `tools/sound/music_bed.py main|trailer` → `mix.py … --music audio/stems/<which>-music.wav`. A project that writes its own mix runs the same three steps.
- Loop at the indexed seam with a crossfade (or trim) → 1–4 kHz speech-pocket dip → duck keyed by my voice (holds through my pauses, slow release, rises only in real gaps) → fade in, and out after my last word.
- **Level:** the median gap while I speak is the House target; then the bed is lowered until the **worst** window clears the fail level (≤ 3 rounds, else blocker). Quiet trailing words can set the level, leaving the median well above target.
- Values used go to `work/config/sound_music.json`; a twin reuses the English `params`.

## Voice-safety checks (Deliver, after the final render)
`gpu-run vt-python tools/qa/voice_over_music.py <project> <out/video.mp4>` for each deliverable; a failure is a blocker. `--mix-transcript inspect/<stem>/report.json` reuses the fresh video-inspect transcript.
1. **Gap:** voice vs music stem loudness in 400 ms windows where words say I speak; median, worst, time, beat. Stale or missing stems fail. **This is the check that protects my voice.**
2. **Clarity:** Whisper must hear in the mix every word it **reliably** hears in the voice stem (same model, settings, language). Reliable = also heard when the voice is 0.5 dB quieter and 50 ms later; a loss must repeat on a second pass of the mix. It's a backstop: Whisper heard every word through noise 10 dB louder than my voice, and failed at 20 dB.
3. **Master:** House loudness and true peak on the final file.

It writes `work/qa/voice_over_music_<which>.json` and one `**Music QA:**` log line. The fresh final visual QA is unchanged.

## After the final render
`vt-python tools/music/finalize.py <project>`: adds a required credit line to the English `out/<name>_social.json` descriptions (YouTube first; it never rewrites other text, and reports fields where it doesn't fit) and updates `used_in` / `last_used`. Commit `music/index.md` with the components and icons. Claude never writes the credit.

**Gotchas**
- One Whisper pass can't be compared with one other: 0.5 dB alone changed 9 of 87 words of a cut voice. Never drop the control passes.
- Raising the voice is never the fix for a failed gap; lower the bed or change the track.
- A rebuilt voice stem or re-mix after the bed makes the stem stale: rerun `export_sfx.sh`, render the audio again, recheck.
