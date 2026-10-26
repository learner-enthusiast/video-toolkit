# video-toolkit

Instructions only, with no code. These Markdown files tell Claude how to build coding videos (16:9) and reels (9:16) when a video needs them.

**Start a new video**
1. Open Claude Code in this folder and run `/setup` once per machine.
2. Run `/new-video <name>`, then drop footage into `projects/<name>/raw/` and screenshots/clips into `assets/`.
3. Fill `projects/<name>/script.md` from a file in `templates/`.
4. Run `/coding-video <name>` or `/reel <name>`. Claude stops at the rough cut for your OK.

`CLAUDE.md` holds the standing rules, `brand.md` the look, `components/` and `pipeline/` the building blocks.
