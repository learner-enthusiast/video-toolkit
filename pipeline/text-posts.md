# Text posts (LinkedIn + X)

**Goal:** for every video, extra standalone posts for LinkedIn and X, written in full and ready to paste as they are, plus the LinkedIn photo. These are **additions**: I still post the video itself on LinkedIn and X with its captions from `<name>_social.json` (`pipeline/social-copy.md`), exactly as before. The text posts are separate posts on the same topic, because photo + text and text-first posts reach people the video doesn't. The steps are in `/text-posts` (`.claude/skills/text-posts/SKILL.md`), the photo layout in `components/specs/LinkedInPhoto.md`.

**When:** the very last step of Stage 4 · Deliver of every video (reel and long-form), after the video deliverables are finished and reported. The video, trailer, SRTs, thumbnail, social JSON and carousel never wait for it, and a problem here never blocks them. Also on its own for older projects (`/text-posts <project>`).

**Source**
- `script.md` only (plus logos from `icons/`), never the transcript, same as the carousel. Never invent a fact, number or claim the script doesn't say. Shorten and reorder; don't add.
- Use the script's glossary spellings exactly.
- Same core idea as the video, but not a copy of the video's caption, and each post must stand alone: a reader who never sees the video still learns the whole point.

## LinkedIn: one photo + a long text post

**Post** (`linkedin_post.txt`), in this exact shape:

```
<hook line: the boldest claim, number or result, ≤ ~110 chars>
<optional 2nd line that adds tension; both lines sit above "see more">

<1–2 lines of context: the situation, why it matters>

1. <point>: <explained properly in 1–3 short lines, not just named>
2. <point>: ...
3. ...
(4–7 points)

<takeaway: 1 line, my opinion>

<one specific question that invites a real answer>

#tag1 #tag2 #tag3
```

- First person, plain words, professional but human. One idea per point, and each point explains the how or why with the script's example or number; a list of bare labels fails.
- A blank line between blocks; points numbered `1.` `2.` (or `→` if the order doesn't matter). LinkedIn shows no markdown: no `**bold**`, no `#` headings, no emojis.
- Length 1,200–2,500 characters (hard limit 3,000). 3–5 specific hashtags at the end only.
- No external link in the post body (it cuts reach). If there's a video or source to link, put it in `linkedin_first_comment.txt` ("Full video: <url>"), which I post as the first comment.
- The question is specific ("Would you cache this at the edge or in Redis?"), never "Thoughts?" or "Agree?".

**Photo** (`linkedin_photo.png`, 1080x1350, 4:5): the scroll-stopper that makes people read the post. Content, not my face. Spec: `components/specs/LinkedInPhoto.md`.
- It carries the hook as a picture: one short headline (≤ 8 words) plus one supporting visual from the script (the key number, a before/after, a small diagram, a code snippet, a chart).
- It works with the post's first line, not as a copy of it: the photo makes the claim visible, the first line makes people click "see more".
- It reads on a phone: downscale to 270x338 and the headline and the visual's point are still clear.
- Alt text in `linkedin_photo_alt.txt` (one line: what it shows and says).

## X: a text post and an Article (I have X Premium)

**Post** (`x_post.txt`): always written. I have X Premium, so it may go past 280 characters, but it stays a post, not an essay: 280–1,000 characters, and the first 280 must work on their own (that's what shows before "Show more"). If `CLAUDE.md` ever says X Premium: no, the whole post is ≤ 280.
- Line 1 is a specific claim with a number or a concrete result from the script. No warm-up.
- Then the one idea, in 2–4 short lines with line breaks. No bullets clutter, no thread unless the prompt asks.
- End with my take or a question someone can actually answer.
- 0–1 hashtag. No "like/repost/follow" asks (X treats soliciting engagement as against its creator rules).
- Text only: no image or video attached unless the prompt says so. A link to the video goes in `x_reply.txt` (posted as the first reply), so the post stands alone.
- Count characters with code (`len()` on the exact text): ≤ 1,000 total, and check where character 280 falls so the cut lands after a complete thought.

**Article** (written for every video while `CLAUDE.md` says X Premium: yes; Articles need Premium). Write `x_article.md` and `x_article_header.png`, following X's own "Ultimate guide to Articles on X" (@XCreators, Jan 2026):
- **Purpose first:** one line at the top of the file (not published) saying what the reader should feel, think or do after reading.
- **Title:** specific, sparks curiosity and promises value ("Why 95% of productivity advice fails", not "Tips for better productivity"). **First sentence** is a hook that pulls the reader in.
- **Header image** (`x_article_header.png`): relevant and visually strong, same look as the LinkedIn photo, in a wide 5:2 frame (1500x600). Check the crop in X's composer before posting.
- **Skimmable on mobile:** paragraphs 2–4 lines max, one idea per paragraph, a subheading every 3–5 paragraphs, bullets or numbered lists over walls of text, the key insight in bold in almost every section.
- **Voice:** natural and recognisable, talking to "you" like a friend, not a textbook.
- **Show, don't tell:** every claim is followed straight away by the script's example, number or incident.
- **Edit ruthlessly:** after the first draft, cut 20–30% and read it back word by word as if aloud; the second draft is for the reader.
- **Formatting and images:** use images, code blocks and quotes where they explain better. An embedded post of mine can serve as a live example.
- **Strong ending:** a short summary plus a question or a clear next step.
- **Launch notes** (`x_article_launch.txt`, for me, not published): a teaser post before publishing; after publishing, a quote post with a 3–5 bullet "table of contents" preview; pin the Article for the first 24–72 hours; reply to early comments; a week later, a thread teaser from the best section.

## Output (`out/text-posts/`)

```
linkedin_photo.png            1080x1350 hook photo
linkedin_photo_alt.txt        alt text, one line
linkedin_post.txt             the full post, paste as-is
linkedin_first_comment.txt    only if there's a link to share
x_post.txt                    280–1,000 chars (Premium), paste as-is
x_reply.txt                   only if there's a link to share
x_article.md                  the full Article, paste as-is
x_article_header.png          1500x600 header
x_article_launch.txt          launch notes, for me
```

These files are separate from `<name>_social.json`: never copy them into it or change its LinkedIn/X video captions.

**Build (photo)**
- Reuse the project's Remotion setup in `work/remotion/` (theme, fonts, logos in `public/`): add `src/text-posts/`, register `Still`s `LinkedInPhoto` and `XArticleHeader`, render with the bundle-once script. If there's no `work/remotion/`, create a blank one per `pipeline/composition.md` → Setup.
- Photo text lives in `work/text-posts/photo.json` (written from the approved draft), never typed into the component.
- Render on the GPU (`gpu-run`, `--gl=angle`), or the CPU (`--gl=swangle`) if the GPU is busy, and say so.

**QA** (Claude opens the PNG and reads every text file; nothing passes unlooked-at)
- Photo: 1080x1350 exactly; no face; headline ≤ 8 words; nothing clipped or outside the 80 px margin; headline still readable and the visual's point clear at 270x338; brand colours, fonts, border and radius from `brand.md`; no red/green, no emojis; logos official and uncropped.
- LinkedIn post: the shape above, in order; hook ≤ ~110 chars; 4–7 points, each explained; 1,200–3,000 chars; no link, no markdown, no emojis; 3–5 hashtags at the end; ends on a specific question.
- X post: 280–1,000 chars counted in code, the first 280 a complete thought (≤ 280 total if Premium is no); line 1 has a number or concrete result; no engagement asks; ≤ 1 hashtag; no link in the body.
- Article: title specific; first sentence a hook; no paragraph over 4 lines; a subheading at least every 5 paragraphs; a bold insight per section; every claim backed by an example from the script; ends with summary + question/CTA; header 1500x600.
- Facts: diff every number, name and claim in all files against `script.md`.