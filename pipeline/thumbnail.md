# Thumbnail

**Goal:** a concept-first cover that reads at phone size and rewards a second look: the headline, a picture of the video's idea, and me with the mic. Layout, patterns and per-brand looks: `components/specs/Thumbnail.md`.

**Source photo**
1. **Check for my photo first:** any image in the project's `raw/` whose name contains "thumb" (`thumbnail_raw.*`, `rawthumbnail.jpg`, …; jpg, jpeg, png or webp). Glob `raw/*thumb*`, and look again at Deliver: I may drop it in after Prep (`system-design-of-ai/05-model-routing`).
2. **If it exists, it's the base image.** It's a deliberate still, so it's sharper and better posed than any video frame.
   - Don't extract a frame from the talking-head video.
   - Cut me out (background removal) only if the layout needs it, on a copy in `work/`; `raw/` stays untouched.
   - Keep the face natural: no warping, reshaping or heavy filters.
3. **If it doesn't, fall back to the video:** the sharpest frame with eyes open, mouth closed or mid-smile, and no motion blur (see The cutout).
4. **Build the design around the video's content either way.** Pull the topic, key visuals and on-screen graphics (logos, charts, code, screenshots) from the video and `script.md`. Add the video's motion-style accents (arrows, glows, highlight blocks) so the still echoes its animations.
5. **Follow `brand.md`** and the video's `brands/brand-N.md` for fonts, colors and layout. A thumbnail always follows its video's brand.
6. **Export** the recommended variant. Reel (≤ 2:59): the cover `out/thumbnail_9x16.png` at 1080x1920 only, no 1280x720. Long-form (> 3:00): `out/thumbnail.png` at 1280x720, plus `out/thumbnail_9x16.png` at 1080x1920 for its 9:16 trailer.

**Plan before pixels**
Write `work/thumbnail_plan.md` with:
- **Headline:** from the hook, a question or a why/how claim, ≤ 7 words, split into lines.
- **`hl`:** the key phrase.
- **Pattern:** one from the spec, and the **texture**.
- **Scene elements:** 4–8, one of them focal. Tie each to a beat and give its source: a library component + payoff frame, a logo file in `icons/`, or a capture URL.
- **Last two covers:** their patterns (from sibling projects' `work/thumbnail_plan.md`; if there's none, look at their cover), to show this one differs.

Show me the plan and wait for my OK before building.

**Build the scene from the video itself**
- Use the same library components the video used, frozen at their payoff frame (`<Freeze frame={n}>`).
- Take official logos from `icons/` (`icons/icons.md`).
- Capture real pages with Playwright (`pipeline/web-capture.md`).
- Compose the still from `src/lib/Thumbnail.tsx` (`templates/remotion/Thumbnail.tsx`): 1080x1920 only for a reel; 1280x720 and 1080x1920 for long-form.

**The cutout**
- No `thumbnail_raw`: pick 5–8 candidate frames from the final edit (eyes open, mouth closed or mid-smile, sharp, face fully lit). Look at each and keep the best 2–3.
- Cut me out with rembg `birefnet-general` on a copy, to a PNG with alpha. Clean the hair edge if it's ragged, and union the mic mask if parts are missing (`tools/thumbnail/mic_union.py`).

**Variants**
- Make 3 that differ in pattern, headline or focal element, not just color: `out/thumbnail/thumb_a.png`, `thumb_b.png`, `thumb_c.png`.

**DIY kit for ChatGPT**
Also give me what I need to make my own thumbnail in ChatGPT (image generation), in the same `out/thumbnail/` folder:
- **Static assets, max 3**, copied as PNGs into `out/thumbnail/assets/` with clear names, for example:
  1. `01_me_cutout.png`: my best cut-out frame (transparent background, sharp, eyes open).
  2. `02_<logo-or-tool>.png`: the logo or icon of the main tool or language.
  3. `03_<screen>.png`: one key screenshot or result frame from the video.
  Pick only what helps the thumbnail; fewer is fine. Copies only, never move or edit `raw/` or `assets/`.
- **`out/thumbnail/chatgpt_prompt.md`** with:
  - A one-line "how to use": open ChatGPT, attach the files in `assets/`, paste one prompt.
  - **Claude's prompt:** a ready-to-paste prompt written from the final video's content. It names each attached asset by file name and says how to use it. It gives the size and aspect (reel: 1080x1920, 9:16 only; long-form: 1280x720, 16:9) and describes the same anatomy as the spec, element by element:
    - the badge text and its place;
    - the exact headline, line by line, with the accent phrase on its skewed block and the three sparks;
    - each scene element, its label and its position around the head;
    - the focal element's glow and ring;
    - the video's brand: its hex colors, background and texture (from `brands/brand-N.md`);
    - the 3:4 safe area: everything important between y 240 and 1680, nothing in the bottom-right corner;
    - "keep the face from image 1 unchanged".
  - **Your own prompt:** a short fill-in template (headline, pattern, scene elements, colors) that uses the same attached assets, so I can write my own instead.
  - A line saying ChatGPT may alter the face, and to ask it to keep the face from image 1 exactly as it is.

**Checks** (through the vision subagent, `vision-qa`)
- At 180x320, and on the 3:4 crop (y 240–1680) at 270x360: the headline reads, my face is recognisable, and the idea's shape is clear in one second. Long-form 16:9: at 320x180.
- At full size: the scene holds at least 4 real details.
- Generic test: "could this scene belong to any video on this topic?" If yes, add the video's own numbers, labels, logos or captured page.
- Nothing important outside y 240–1680, and no text in the bottom-right corner (the duration badge).
- Under 2 MB, PNG or high-quality JPG.

**Report**
- Show me all three and recommend one with a one-line reason.
- List the assets in the ChatGPT kit and where the prompt file is.

**Gotchas**
- Check the headline against the head box at phone size: ≤ 3 lines of about 14 characters, ending above the hair.
- Cut out with `birefnet-general`; `birefnet-portrait` drops the mic. In 16:9, fade or crop a cutout edge that reaches the photo frame.
- **The whole mic and boom arm are always in the thumbnail, recognisable at 180x320.** Have vision list the parts that survived the cutout.
- Missing mic parts: segment the mic region alone and union it (`tools/thumbnail/mic_union.py`); arm off the canvas edge, feather only the other side, place from the head top.
- Never run rembg/birefnet (~9 GB RAM) beside a Remotion render.
- Rasterise SVG logos with `cairosvg` (ImageMagick can output blank) and check alpha mean > 0.
