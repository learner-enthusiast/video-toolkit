# Render

**Goal:** a ProRes master per composition, then a delivery MP4 at -16 LUFS.

**Master**
- Render through `gpu-run` to `work/render/<comp>.mov` with ProRes standard, `--gl=angle`, and concurrency of about cores/2.
- Render a 10 s range first (`--frames`) and look at it before committing to the full length.
- Logs go to `work/logs/render-<comp>.log`.

**Delivery encode**
- Mux the master's picture with the voice/mix WAV, passed separately so the audio is sample-exact.
- Two-pass `loudnorm` to I=-16, TP=-1.5, LRA=11: measure, then apply with the measured values and `linear=true`, resampled to 48 kHz.
- Video: `h264_nvenc -preset p6 -tune hq -rc vbr -cq 19 -b:v 0 -maxrate 20M -profile:v high`, with `yuv420p` at 30 fps. Without NVENC, use libx264 veryfast crf 20.
- Audio: AAC 192k. Add `-movflags +faststart`.
- Name outputs `out/<name>_16x9.mp4`, `out/<name>_trailer_9x16.mp4`, and so on.

**Checks**
- `ffprobe` the output: codec, size, fps, duration matching the composition, audio present.
- Loudness of the final file is about -16 LUFS (`ebur128`).

**Gotchas**
- Check the voice WAV's start offset against the timeline. A mis-laid voice track once started 2.5–4 s late, and only the A/V check in `qa.md` caught it.
- Keep masters until I approve the finals, so re-encoding never means re-rendering.
