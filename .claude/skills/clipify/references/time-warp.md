# Time-warping reveals (Step 4c)

Moved verbatim from `SKILL.md` (token diet, 2026-11-20). Load only when this path is used.

## Step 4c — Time-warping reveals (optional)

When the user wants a slow scenic / pan / reveal shot tightened ("cut this in half") without losing the arc, speed-ramp instead of trimming. Trimming forces you to drop part of the arc; speed-ramping preserves all the beats at higher tempo.

```bash
# 2x speed: render video only. If speech is present, time-warp a segment from the verified cleaned WAV with atempo=2.0 and mux it; never retain source-video audio.
ffmpeg -y -ss "$START" -i "$CLIP" -t "$ORIG_DUR" \
  -vf "setpts=PTS/2,scale=1080:1920:flags=lanczos,fps=30" \
  -an \
  -c:v h264_nvenc -preset p5 -rc vbr -cq 21 -b:v 0 -pix_fmt yuv420p \
  projects/<name>/work/clipify/clip_2x.mp4
```

Rules of thumb:

- **1.5x** — human movement that should feel "slightly brisk" without looking sped up
- **2x** — punchier reveal; still reads as natural
- **3x–4x** — time-lapse vibe (chain `atempo=2.0,atempo=2.0` for 4x; `atempo` accepts only 0.5–2.0 per filter instance)
- Drop `-af atempo` and mute the segment if the audio is just ambient/wind and the chipmunking would be distracting

Useful when the rest of the cut is rhythmic (chop montage, chat back-and-forth) and the reveal would otherwise feel like a dead spot.

