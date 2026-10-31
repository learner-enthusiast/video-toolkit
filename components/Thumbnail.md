# Thumbnail

**Purpose:** a still composition for the video thumbnail (or reel cover). The steps are in `pipeline/thumbnail.md`.

**Props:** `cutout` (my PNG with alpha), `headline` (2–5 words), `accentVisual` (an icon, screenshot crop or number), `side`, `size` (1280x720 | 1080x1920).

**Look**
- Brand background with a soft accent radial glow behind me.
- My cutout fills about 45% of the width, cropped at the chest, with a subtle 2–3 px light rim so I separate from the background.
- Headline in Inter 800 at 110–140 px, at most 2 lines, white with one key word in accent. High contrast and no thin weights.
- One accent visual (a big number, an icon cluster or a tilted screenshot card) on the free side.

**Rules**
- 9:16: the cutout's head must start below the headline and accent visual (about y ≥ 800 of 1920), or the face covers the text. Check at 180x320.
- Cut out with rembg `birefnet-portrait`: much cleaner ears and shoulders than `u2net_human_seg` on busy phone backgrounds.
- Place the cutout from its alpha bounding box (hair-top y × scale), not from another video's numbers: how far I sit from the phone changes it. On `bloom-filter` the copied placement put my head at y≈500 over the accent; hair top at y≈830 fixed it.
- Show one idea; it must read at 320x180.
- Keep text out of the bottom-right corner (the duration badge).
- Give the face a clear expression and good light; lift exposure on the cutout if needed.
- Use no emojis, no clip-art arrows or circles, and no more than 3 colors. Brand-style accents from the video's own animations (orange arrows, glows, highlight blocks) are fine (`pipeline/thumbnail.md`).
