# Render

**Goal:** a ProRes master per composition, then a delivery MP4 at House numbers loudness (`CLAUDE.md`).

**Master**
- Render through `gpu-run` to `work/render/<comp>.mov` with ProRes standard, `--gl=angle`, and concurrency of about cores/2.
- Render a 10 s range first (`--frames`) and look at it before committing to the full length.
- Logs go to `work/logs/render-<comp>.log`.

**Delivery encode**
- Mux the master's picture with `work/audio/mix.wav` (voice + SFX + ducked music, `pipeline/sound.md`; the trailers use their own `mix_trailer_*.wav`), passed separately so the audio is sample-exact. The master's own audio isn't used.
- Two-pass `loudnorm` to I=-16, TP=-1.5, LRA=11: measure, then apply with the measured values and `linear=true`, resampled to 48 kHz.
- Video: `h264_nvenc -preset p6 -tune hq -rc vbr -cq 19 -b:v 0 -maxrate 20M -profile:v high`, with `yuv420p` at 30 fps. Without NVENC, use libx264 veryfast crf 20.
- Audio: AAC 192k. Add `-movflags +faststart`.
- Name outputs in `projects/<name>/out/`. Reel (≤ 2:59): render only 1080x1920: `<name>_9x16.mp4` and `<name>_trailer_9x16.mp4`; no 16:9 render or encode. Long-form (> 3:00): `<name>_16x9.mp4`, `<name>_trailer_16x9.mp4`, `<name>_trailer_9x16.mp4`.

**Tool:** `tools/jobs/render_chain.sh [comp ...]` from `work/` does both steps for every comp in `config/render_chain.json` (`{"outputs": {"Main": {"name": "<name>_9x16", "mix": "audio/mix.wav"}}}`), prints loudness, probe and decode checks, and exits non-zero if a render or encode failed. Run it in a batch (`pipeline/delegation.md` §5). `tools/jobs/gpu_wait.sh <cmd>` waits for a shared GPU and retries on OOM.

**Checks**
- `ffprobe` the output: codec, size, fps, duration matching the composition, audio present.
- Loudness of the final file meets `CLAUDE.md` → House numbers (`ebur128`).

**Gotchas**
- Stop a render by PID (`pgrep -f 'remotion render'`, `kill <pid>`), never `pkill -f` (it matches your own shell and other projects).
- Check the voice WAV's start offset against the timeline (A/V check in `qa.md`).
- Keep masters until I approve the finals.
- A `-loop 1` input never ends: add `shortest=1` to every framesync filter and cap with `-frames:v`.
- Never edit a script while a job is running it (bash reads as it goes): edit a copy or wait.
- Project folders may be renamed with shell characters: derive paths, never hard-code them, and quote every path.
- Many `OffthreadVideo` segments can OOM: `--offthreadvideo-cache-size-in-bytes=2000000000`, `--concurrency=3`, check `free -h` for other renders.
- Run render chains only through `tools/jobs/batch.sh`; before any manual re-run `pgrep -f <chain>`; decode-check every delivery (`ffmpeg -v error … -f null -`).
- Pass `--timeout=120000` (stills: `timeoutInMilliseconds`): seeking a large working copy can exceed the 28 s default.
