# Action mode (Step 1B)

Moved verbatim from `SKILL.md` (token diet, 2026-11-20). Load only when this path is used.

## Step 1B — Find each strike (action mode)

Replace Whisper with audio-transient detection. The detector finds sharp impacts (axe-on-wood, fist-on-pad, drumhead, ball-on-bat, wood landing on a pile) by computing spectral flux on the 1–6 kHz band — the broadband impulse an impact creates that ambient/wind doesn't.

```bash
ffmpeg -y -hwaccel cuda -i "$VIDEO" -vn -ac 1 -ar 16000 projects/<name>/work/clipify/audio.wav
vt-python <skill-dir>/scripts/detect_transients.py projects/<name>/work/clipify/audio.wav \
  --min-flux 30 --min-gap 0.6 > projects/<name>/work/clipify/strikes.json
```

Tuning:

- `--min-flux 30` is the sane default. Real impacts register 50–300; ambient/wind sits at 5–15. Too many false positives → raise to 40–50. Too few hits → drop to 20.
- `--min-gap 0.6` (seconds) is the closest two strikes can be. Fast drumming may need 0.2; chopping is fine at 0.6–1.0.
- `--band 1000:6000` covers wood/metal/glass impacts. Heavy thuds (kick drum, body shots) live lower (`--band 200:2000`); whistles/clinks/snare cracks higher (`--band 4000:10000`).
- For multi-clip sources (a folder of phone clips), run the detector on each clip and pick a varied set across angles. Aim for 50–65 strikes for a 45–60s montage at ~0.9s per shot.

Each "shot" should start ~0.4s before the strike (showing wind-up) and end ~0.5s after (strike + brief follow-through). That's ~0.9s per beat.

