# Split-screen (Step 4b)

Moved verbatim from `SKILL.md` (token diet, 2026-11-20). Load only when this path is used.

## Step 4b — Split-screen (both faces always visible)

Two stacked tiles, 1080×960 each. The active speaker's tile is on top — overlay flips at speaker changes.

```
[0:v]split=2[a0][a1];
[a0]crop=Wcrop:Hcrop:LX_tile:LY_tile,scale=1080:960,split=2[lt0][lt1];
[a1]crop=Wcrop:Hcrop:RX_tile:RY_tile,scale=1080:960,split=2[rt0][rt1];
[lt0][rt0]vstack[layoutL];
[rt1][lt1]vstack[layoutR];
[layoutL][layoutR]overlay=0:0:enable='<RIGHT_SPEAKER_ENABLE>'[v]
```

Build `<RIGHT_SPEAKER_ENABLE>` from `segments.json` as `between(t,a,b)+between(t,a,b)+...` over the right-speaker segments. Tile crops should target ~720×640 around each face (1.125:1 to match 1080×960).

Render this layout video-only (`-an`), then mux the matching clip segment from the verified cleaned WAV. Never carry audio from `clip.mp4` or `$VIDEO` into the edited output.

