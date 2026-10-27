# Social copy

**Goal:** one JSON file with ready-to-paste titles, captions and hashtags for every platform, so I can upload and copy-paste.

**Source**
- Write from what the final video actually says (the final transcript and beat list), plus what I asked for in my prompt. Never promise something the video doesn't show.
- Same core message everywhere, rewritten for each platform's tone. No clickbait the video can't back up.
- Hashtags: specific and relevant (tech, language, tool names) over generic ones. No spaces inside a tag.

**Platform rules**
- **LinkedIn:** professional, first-person. A hook line, 3–6 short lines of value, a CTA. Under 1,300 chars so it reads well before "see more". 3–5 hashtags at the end.
- **X:** short. The whole post including hashtags ≤ 280 chars, with 1–2 hashtags. Only if I say I have X Premium, also write a longer `post_long` (up to ~1,000 chars).
- **Instagram:** hook in the first line (it's cut at ~125 chars), short caption, a CTA. 5–10 hashtags in a separate field. Total ≤ 2,200 chars.
- **Facebook:** conversational, 1–3 short paragraphs, 2–4 hashtags.
- **Threads:** casual, ≤ 500 chars including hashtags, 1–3 hashtags.
- **YouTube:** title ≤ 70 chars with the main keyword near the front. Description: a 2-line summary first (shown above "more"), then what you'll learn, then chapters from the beat timestamps (`00:00 Intro` first, each chapter ≥ 10 s, at least 3), then links, then 3–5 hashtags (the first 3 show above the title). Also give `tags` (comma-separated keywords, ≤ 500 chars total) and a 9:16 `shorts_title` for the portrait trailer, ending in `#shorts`.

**File**
- Write `out/<name>_social.json`, UTF-8, valid JSON (parse it to check). Use `\n` for line breaks inside strings.

```json
{
  "video": "<name>",
  "files": {
    "main": "<name>_16x9.mp4",
    "trailer_landscape": "<name>_trailer_16x9.mp4",
    "trailer_portrait": "<name>_trailer_9x16.mp4",
    "thumbnail": "thumb_a.png"
  },
  "linkedin":  { "post": "", "hashtags": [] },
  "x":         { "post": "", "hashtags": [], "post_long": null },
  "instagram": { "caption": "", "hashtags": [] },
  "facebook":  { "post": "", "hashtags": [] },
  "threads":   { "post": "", "hashtags": [] },
  "youtube": {
    "title": "",
    "description": "",
    "tags": [],
    "hashtags": [],
    "shorts_title": ""
  }
}
```

- `hashtags` are arrays with the `#`. Each `post`/`caption` already ends with its hashtags, so it can be pasted as-is.
- `thumbnail` names the variant I'd pick (the one recommended in `thumbnail.md`).

**Checks**
- Count characters for X, Threads and the YouTube title and fix anything over the limit.
- Chapter timestamps match the final main video, not the rough cut.
