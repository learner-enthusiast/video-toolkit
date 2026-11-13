# video-toolkit

Instructions only, with no code. These Markdown files tell Claude how to build coding videos (16:9) and reels (9:16) when a video needs them.

**Start a new video**
1. Open Claude Code in this folder and run `/setup` once per machine (manual steps: `setup.md`).
2. Run `/new-video <name>`, then drop footage into `projects/<name>/raw/` and screenshots/clips into `assets/`.
3. Fill `projects/<name>/script.md` from a file in `templates/`.
4. Run `/coding-video <name>` or `/reel <name>`. Claude stops at the rough cut for your OK.
5. Collect everything from `projects/<name>/out/`: the main video, one trailer cut in landscape and portrait (a short cut you define in the prompt, else the default trailer; never both), SRTs, `thumbnail/` (rendered thumbnails plus a ChatGPT prompt and up to 3 assets to make your own), `<name>_social.json` with copy-paste posts and hashtags for every platform, and for reels `carousel/` (6–8 Instagram slides, a PDF, caption and alt text; `/carousel <name>` also works on older projects).

**Layout.** Every beat is HEAD (face fills the frame), FULL (graphic fills the frame) or SPLIT (graphic on top, face below). There is no default; the script's `[mm:ss–mm:ss | STATE]` cues are the plan, and Claude may improve them as a creative co-director within the rules in `CLAUDE.md`.

## Playlists

Videos can belong to a series. Run `/new-video <topic>` and answer "Which playlist? (or none)". For a playlist, the episode goes in `projects/<playlist>/<NN>-<topic>/` (next number, same `raw/ assets/ script.md work/ out/` structure, gitignored) and Claude reads the tracked series rules in `series/<playlist>.md`. First playlist: **System Design of AI** (`series/system-design-of-ai.md`; first episode `projects/system-design-of-ai/01-streaming/`). Its topics live in my sheet "AI System Design Shorts – 110 Topics".

`projects/<name>/log.md` keeps a dated history of every prompt, what Claude changed, how long it took, and the tokens used.

`CLAUDE.md` holds the standing rules, `brand.md` the look, `components/` and `pipeline/` the building blocks.
