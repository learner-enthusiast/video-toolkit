---
name: new-video
description: Scaffold projects/<name>/ with raw/, assets/, script.md, work/ and out/.
argument-hint: <name>
---

# New video

1. Take `<name>` from the arguments (kebab-case). If it is missing, ask for it. If `projects/<name>/` already exists, stop and tell me.
2. Create:
   - `projects/<name>/raw/` for my recordings (read-only after I drop them in)
   - `projects/<name>/assets/` for screenshots, clips and logos (read-only)
   - `projects/<name>/work/logs/` for everything intermediate
   - `projects/<name>/out/` for the deliverables
   - `projects/<name>/script.md`
   - `projects/<name>/log.md`, headed `# <name> log`, with this scaffolding as its first entry (see `pipeline/project-log.md`)
3. Ask which kind of video: tutorial, project demo, or reel. Copy the matching file from `templates/` into `script.md`, and copy `templates/shotlist.md` into `work/shotlist.md`.
4. Copy `.env` into the project only if I ask. It is gitignored either way.
5. Tell me where to drop the files and which skill to run next (`/coding-video` or `/reel`).

Do not create the Remotion project here. `pipeline/composition.md` does that after the rough cut is approved.
