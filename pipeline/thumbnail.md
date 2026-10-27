# Thumbnail

**Goal:** a thumbnail that reads at phone size. See `components/Thumbnail.md` for the layout.

**Do**
- Pick 5–8 candidate frames of me from the final edit: eyes open, mouth closed or mid-smile, sharp, face fully lit. Look at each and keep the best 2–3.
- Cut me out with `rembg` (person model) on a copy, to a PNG with alpha. Clean the hair edge if it is ragged.
- Build the `Thumbnail` composition as a Remotion still (1280x720; 1080x1920 for reels).
- Make 3 variants that differ in one thing each (headline wording, side, or accent visual). Render them to `out/thumbnail/thumb_a.png`, `thumb_b.png`, `thumb_c.png`.

**DIY kit for ChatGPT**
Also give me what I need to make my own thumbnail in ChatGPT (image generation), in the same `out/thumbnail/` folder:
- **Static assets, max 3**, copied as PNGs into `out/thumbnail/assets/` with clear names, for example:
  1. `01_me_cutout.png`: my best cut-out frame (transparent background, sharp, eyes open).
  2. `02_<logo-or-tool>.png`: the logo or icon of the main tool or language.
  3. `03_<screen>.png`: one key screenshot or result frame from the video.
  Pick only what helps the thumbnail; fewer is fine. Copies only, never move or edit `raw/` or `assets/`.
- **`out/thumbnail/chatgpt_prompt.md`** with:
  - A one-line "how to use": open ChatGPT, attach the files in `assets/`, paste one prompt.
  - **Claude's prompt:** a ready-to-paste prompt written from the final video's content. It names each attached asset by file name and says how to use it ("use image 1 as the person, keep the face unchanged"). It gives the size and aspect (1280x720, 16:9; 1080x1920, 9:16 for reels), the exact headline (2–5 words), the layout and side, the colors from `brand.md`, high contrast, readable at phone size, and nothing in the bottom-right corner.
  - **Your own prompt:** a short fill-in template (headline, mood, layout, colors) that uses the same attached assets, so I can write my own instead.
  - A line saying ChatGPT may alter the face, and to ask it to keep the face from image 1 exactly as it is.

**Checks**
- Downscale each to 320x180 and look at it. The headline must be readable, the face recognizable, and the subject clear in under a second.
- No text in the bottom-right corner (platform timestamp badge).
- Under 2 MB, PNG or high-quality JPG.

**Report**
- Show me all three and recommend one with a one-line reason.
- List the assets in the ChatGPT kit and where the prompt file is.
