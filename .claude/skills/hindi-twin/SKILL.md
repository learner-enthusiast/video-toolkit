---
name: hindi-twin
description: Make the Hindi twin of a delivered English reel with the same composition (Hindi voice, face footage, cue times and tool-made Roman Hindi captions).
argument-hint: <english-project-name>
disable-model-invocation: true
---

# Hindi twin

Follow `pipeline/hindi-twin.md`; read only the section for the current session. Opener, close, pace, length and loudness: `CLAUDE.md` → House numbers.

1. The twin is `projects/<name>-hi/`. If it doesn't exist, create it (`tools/twin/new_twin.py`).
2. **Run the gate first** (`tools/twin/gate.py`). If it refuses, stop and report the reasons. Nothing else runs.
3. Two sessions: **H1 · Prep + Cut** (ends at the rough cut: **stop for my OK**) and **H2 · Map, render, deliver** (only after my OK is in the twin's `log.md`).
4. Never write or edit caption text, transliterations or dictionary entries; run the tools and report what they flag.
5. Never run `/carousel`, `/text-posts`, thumbnail or social-copy steps: a twin ships exactly four files.
6. Log every turn (`pipeline/project-log.md`).
