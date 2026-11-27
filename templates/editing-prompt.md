# Build: <series / title> (<9:16 reel | long-form 16:9>)

> **Final video ≤ <2:59>. Speed-up cap <1.4x>.** <one line: script word count / expected pace, if useful>

**Project:** `projects/<name>/` (or `projects/<playlist>/<NN>-<topic>/`; create it with `/new-video` if missing).
**Brand:** <1 | 2 | 3> (brand.md)
**Raw:** <where the talking head is; never modify `raw/`>.
**Music:** <id | music/tracks/<file> | none | audition [id1,id2,id3]> (delete the line for ★house rotation)
**Notes:** <series + episode, exceptions for this video, special assets/logos to reuse or download, caption spellings, number formatting, accent-highlight words, the 3 approval stills, components to build or extend, series-file updates>.
**GPU:** `gpu-run` (PRIME offload) for Whisper, renders and encodes; see `CLAUDE.md` → GPU.

Everything else (quality bar, layout states, length rule, never cutting lines, checkpoints, deliverables, logging) is fixed in `/reel` or `/coding-video`.

---

# Script

<paste the script: hook, business case / motifs, beats tagged `[B07 | mm:ss–mm:ss | HEAD|FULL|SPLIT]` (IDs `B01…`, unique, in order) with cues>

## 60-second cut

<the spoken lines of the short cut, in order; this IS the trailer. Leave the section out to get the default trailer from `pipeline/trailer.md`>

# Hindi script

<optional: the romanized Hindi script, one beat per line with the same IDs: `[B07 | SPLIT | tableScan="poori table"] <line>`. English Prep only saves it for the twin. Leave the section out if there is no twin.>

## Hindi 60-second cut

<optional: beat IDs, e.g. B01, B02, B05–B07, B18>
