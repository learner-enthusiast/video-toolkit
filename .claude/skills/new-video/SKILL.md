---
name: new-video
description: Scaffold projects/<name>/ with raw/, assets/, script.md, work/ and out/.
argument-hint: <name>
---

# New video

1. Take `<name>` from the arguments (kebab-case). If it is missing, ask for it.
2. Ask **"Which playlist? (or none)"**. List the playlists in `series/*.md` as options. 
   - **None:** the project folder is `projects/<name>/`.
   - **A playlist:** the folder is `projects/<playlist>/<NN>-<name>/`, where `<NN>` is the next number (two digits) after the highest existing `<NN>-*` folder in `projects/<playlist>/` (01 if none). Read `series/<playlist>.md` now and follow it for this episode (format, characters, length, end card, deliverables). Add the episode to that file's Episodes table if it isn't there.
   - If the folder already exists, stop and tell me.
   Below, `projects/<name>/` means the chosen folder.
3. Create:
   - `projects/<name>/raw/` for my recordings (read-only after I drop them in)
   - `projects/<name>/assets/` for screenshots and clips (read-only). Logos and icons are not stored here: they live in the shared `icons/` library (`icons/icons.md`)
   - `projects/<name>/work/logs/` for everything intermediate
   - `projects/<name>/out/` for the deliverables
   - `projects/<name>/script.md`
   - `projects/<name>/log.md`, headed `# <name> log`, with this scaffolding as its first entry (see `pipeline/project-log.md`)
   - Run `vt-python tools/project_state.py init projects/<name>/` after the folder exists
4. Ask which kind of video: tutorial, project demo, or reel. Copy the matching file from `templates/` into `script.md`, and copy `templates/shotlist.md` into `work/shotlist.md`. Cues in the script use `[B07 | mm:ss–mm:ss | HEAD]`, `[… | FULL]` or `[… | SPLIT]` (`brand.md` Layout; beat IDs `B01…`, unique, in order). Choose components from `components/index.md` first. Set the script's **Aspect** from the target length: ≤ 2:59 is a reel, 9:16 only (main, trailer and cover; no 16:9 anything); > 3:00 is long-form, 16:9 main with a 16:9 + 9:16 trailer. Then offer to draft or tighten `script.md` with `/scriptwriting`.
5. Copy `.env` into the project only if I ask. It is gitignored either way.
6. Tell me where to drop the files and which skill to run next (`/coding-video` or `/reel`).

**Hindi twin** (`/new-video <name>-hi --twin-of <name>`): run `vt-python tools/twin/new_twin.py projects/<name>` instead of steps 1–5 (it sets `twin_of` and `language: hi`), then point me to `/hindi-twin <name>`.

Do not create the Remotion project here. `pipeline/composition.md` does that after the rough cut is approved.
