---
name: text-posts
description: Write the ready-to-paste LinkedIn post and X post for a video, and render the LinkedIn hook photo (1080x1350), into out/text-posts/. Plus the X Article and its header (I have X Premium).
argument-hint: <project>
---

# Text posts (LinkedIn photo + post, X post)

Extra posts, on top of the video: I still post the video on LinkedIn and X with its captions from `<name>_social.json`, unchanged. This skill adds standalone posts on the same topic, written in full and ready to paste as they are, plus the photo that stops the LinkedIn scroll. Runs as the last step of Stage 4 · Deliver of every video, after the video deliverables are reported (they never wait for it) (`pipeline/stages.md`), or on its own for an older project. Read `CLAUDE.md`, `brand.md`, `pipeline/text-posts.md` and `components/specs/LinkedInPhoto.md` first; `brand.md` wins. Pick any visual for the photo from `components/index.md` first.

**Input:** `projects/<project>/script.md` and the logos it names (from `icons/`). If `<project>` is missing or has no `script.md`, stop and tell me.
- Never invent a fact, number or claim the script doesn't say. Shorten and reorder; don't add.
- Use the script's glossary spellings exactly.
- Never touch `raw/` or `assets/`. A new logo goes in `icons/logos/` with a row in `icons/icons.md`; reuse listed ones.

**Steps**
1. **Draft.** Write `work/text-posts/draft.md` with: the LinkedIn post (full text, with its character count), the photo plan (headline with word count, the one supporting visual and which script line it comes from, dark or off-white style), the X post (full text, with its character count from code), and the Article outline (title, first sentence, subheadings). Give 2 alternative hook lines for LinkedIn and for X under each. **Stop and ask me to approve it** (I may pick an alternative hook).
2. **Photo.** Build the renderer (`components/specs/LinkedInPhoto.md`) and render `work/text-posts/stills/linkedin_photo.png`. Open it and check it yourself first, including the 270x338 downscale, then **stop and ask me to approve the look.**
3. **Write and render.** Render `out/text-posts/linkedin_photo.png`, then write every text file listed in `pipeline/text-posts.md` → Output from the approved draft. Write `x_article.md` in full and render `x_article_header.png` (1500x600, same look). Skip both only if `CLAUDE.md` says X Premium: no.
4. **Leave `<name>_social.json` alone:** its LinkedIn/X entries are the video captions. Don't copy these posts into it.
5. **QA:** `pipeline/text-posts.md` → QA. Open the PNG yourself and read every file in full. Fix and re-check anything that fails.
6. **Log** the run in `log.md` (`pipeline/project-log.md`) and report the files plus anything not done as specified.

Rendering is a heavy job (`tools/jobs/batch.sh`, `pipeline/delegation.md`). The writing, the photo design and every judgment stay with Opus.