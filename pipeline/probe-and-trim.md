# Probe and trim

**Goal:** know every source exactly, then make clean, frame-accurate working copies in `work/`.

**Probe**
- Run `ffprobe` on every file in `raw/` and `assets/`. Report resolution, rotation (side data or `rotate` tag), fps (avg vs. r_frame_rate), duration, and audio streams.
- Phone footage is often stored landscape with a 90° rotation flag. Make sure the working copy is upright, and look at a frame to confirm.
- If avg fps ≠ r_frame_rate, the source is VFR. Convert it to constant 30 fps first, which keeps A/V sync stable.

**Trim clips**
- Filenames may carry the range to keep (e.g. `name-03s-10s.mp4` means 3 s → 10 s). Trim to exactly that range.
- Re-encode for frame-accurate cuts; never stream-copy. Strip audio unless it is needed.
- Normalize to the target size (scale and pad, never stretch) at 30 fps, e.g. 60 fps screen recordings → 30.
- Output to `work/clips/<short-name>.mp4`.

**Gotchas**
- Always quote paths: asset names often contain spaces.
- Never write into `raw/` or `assets/`. Make edits (e.g. blurring a third-party email in a screenshot) on a copy in `work/`.
- Record the decisions (rotation, CFR, trims) in `work/logs/probe.md`.

**Checks**
- Every trimmed clip's duration matches its range to within 1 frame.
- One extracted frame per file, viewed: upright, not squashed.
