# Build: <series / title> (<9:16 reel | long-form 16:9>)

> **Final video ≤ <2:59>. Speed-up cap <1.4x>.** <one line: script word count / expected pace, if useful>

**Project:** `projects/<name>/` (or `projects/<playlist>/<NN>-<topic>/`; create it with `/new-video` if missing).
**Raw:** <where the talking head is; never modify `raw/`>.
**Notes:** <series + episode, exceptions for this video, special assets/logos to reuse or download, caption spellings, number formatting, orange-highlight words, the 3 approval stills, components to build or extend, series-file updates>.
**GPU:** `gpu-run` (PRIME offload) for Whisper, renders and encodes; see `CLAUDE.md` → GPU.

Everything else (quality bar, layout states, length rule, never cutting lines, checkpoints, deliverables, logging) is fixed in `/reel` or `/coding-video`.

---

# Script

<paste the script: hook, business case / motifs, beats with `[mm:ss–mm:ss | HEAD|FULL|SPLIT]` tags and cues>

## 60-second cut

<the spoken lines of the short cut, in order; this IS the trailer. Leave the section out to get the default trailer from `pipeline/trailer.md`>
