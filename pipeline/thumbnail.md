# Thumbnail

**Goal:** a thumbnail that reads at phone size. See `components/Thumbnail.md` for the layout.

**Do**
- Pick 5–8 candidate frames of me from the final edit: eyes open, mouth closed or mid-smile, sharp, face fully lit. Look at each and keep the best 2–3.
- Cut me out with `rembg` (person model) on a copy, to a PNG with alpha. Clean the hair edge if it is ragged.
- Build the `Thumbnail` composition as a Remotion still (1280x720; 1080x1920 for reels).
- Make 3 variants that differ in one thing each (headline wording, side, or accent visual). Render them to `out/thumb_a.png`, `thumb_b.png`, `thumb_c.png`.

**Checks**
- Downscale each to 320x180 and look at it. The headline must be readable, the face recognizable, and the subject clear in under a second.
- No text in the bottom-right corner (platform timestamp badge).
- Under 2 MB, PNG or high-quality JPG.

**Report**
- Show me all three and recommend one with a one-line reason.
