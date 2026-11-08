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
- Name outputs in `projects/<name>/out/`: `<name>_16x9.mp4` (or `<name>_9x16.mp4` for a reel), `<name>_trailer_16x9.mp4`, `<name>_trailer_9x16.mp4`.

**Checks**
- `ffprobe` the output: codec, size, fps, duration matching the composition, audio present.
- Loudness of the final file is about -16 LUFS (`ebur128`).

**Gotchas**
- Check the voice WAV's start offset against the timeline. A mis-laid voice track once started 2.5–4 s late, and only the A/V check in `qa.md` caught it.
- Keep masters until I approve the finals, so re-encoding never means re-rendering.
- A looped still input (`-loop 1 -i mask.png`) never ends, so `-shortest` alone doesn't stop a `-filter_complex` encode: one ran for 1 h and wrote 1.4 GB. Add `shortest=1` to every framesync filter (`overlay`, `alphamerge`) and `-frames:v <source frames>` as a hard cap.
- Never edit a stage script while a runner is executing it: bash reads the file as it goes, so the running job picked up half an edit ("JOBS: unbound variable") and skipped every encode (`kafka`). Edit a copy, or wait for the job to finish.
- Project folders may be renamed mid-project with shell-special characters (`oidc` → `oidc-6&7.11.26`). Stage scripts must not hardcode the project path: derive it (`W="$(cd "$(dirname "$0")/.." && pwd)"`) and quote every path, or an unquoted `&` backgrounds half the command. Tell the Haiku runner to `cd` with the quoted path.
- A 1080x1920 portrait source with ~44 `OffthreadVideo` segments grew the Remotion compositor to 8.8 GB and the kernel OOM-killed it at frame 1,350 (`jwt-explained`, while another session's render held 5.6 GB). Pass `--offthreadvideo-cache-size-in-bytes=2000000000` and `--concurrency=3`, and check `free -h` for other projects' renders before starting. Stopping a chain: kill by PID; `pkill -f <project path>` also matches (and kills) your own shell.
- A background render chain can outlive the shell that launched it: on `docker-explained` the notifying shell died (exit 144) while `render_all.sh` kept going, and a manual re-run of its delivery step wrote the same MP4s at the same time. Both "finished" with exit 0 and a valid-looking ebur128, but the files had corrupt H.264 NAL units and an undecodable AAC track (−70 LUFS on re-read). Before re-running any step by hand, `pgrep -f <chain script>`; launch chains with `nohup setsid … &` and wait on their `ALLDONE` marker; verify every delivery with `ffmpeg -v error -i out.mp4 -f null -` (no output = clean).
- Remotion's default 28 s `delayRender` timeout can expire while `OffthreadVideo` seeks a 1.2 GB 1080x1920 NVENC working copy, killing the whole render at frame 0 (`jwt-is-dead`: both trailers, which nest Main several times, and one still batch). Pass `--timeout=120000` to `remotion render` and `timeoutInMilliseconds: 120000` to `renderStill`.
