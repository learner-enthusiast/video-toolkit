# Sound

**Goal:** every visible hit that should sound gets one consistent sound, music (if any) sits under my voice, and the final mix meets `qa.md`.

**Do**

**1 · The kit (sound brand).** Nine synthesized sounds, the same in every video. No downloaded SFX files.

| File | Sound | Length | Used for |
|---|---|---|---|
| `pop.wav` | two sines (660 + 1320 Hz), round | 120 ms | a card or element entrance |
| `soft-pop.wav` | lower, duller pop (520 + 1040 Hz) | 90 ms | list items, staggered |
| `tick.wav` | bright two-tone click (1150 + 2300 Hz) | 50 ms | timers, countdowns, counters |
| `typing-tick.wav` | short noise click with a little tone | 35 ms | code typing |
| `whoosh.wav` | band-limited pink noise, swell then tail | 450 ms | layout switches (brand wipe) |
| `stamp-thud.wav` | 95 Hz body with a fast decay + dull slap | 260 ms | stamps, things landing hard |
| `pen-scratch.wav` | 3–5.5 kHz noise with a fast flutter | 220 ms | underlines, highlights |
| `riser.wav` | 220 → ~900 Hz chirp under swelling noise | 1.2 s | into a big cut (ends on the cut) |
| `sub-boom.wav` | 50 + 100 Hz sines, slow decay | 900 ms | dark punch moments |

**Recipe pattern:** noise or sine → band filter (high-pass + low-pass) → fast attack (1–4 ms fade in) → fast decay (exponential fade out) → optional compressor → fixed volume. UI sounds stay ≤ 300 ms. Every recipe ends in a fade, and every file is calibrated to peak at **−3.0 dBFS**, so loudness in a video comes only from the cue gains below. Noise sources are seeded, so the files are identical on every build.

**Build once, copy per project.** The kit lives in `~/.cache/video-toolkit/sfx/v1/`. Save the script below as `~/.cache/video-toolkit/sfx/v1/build.sh` and run it with that folder as its argument. Each project copies the kit into `work/remotion/public/sfx/` (and reads it from there for the mix). If any recipe changes, build into `v2/` and say so in the toolkit commit; never change `v1` in place, or older projects stop matching.

```bash
#!/bin/bash
# Build the sound kit. usage: build.sh <out-dir>
set -euo pipefail
O="${1:?out dir}"; mkdir -p "$O"
F=(ffmpeg -hide_banner -loglevel error -y)
A=(-ar 48000 -ac 1 -c:a pcm_s16le)

# pop: two sines an octave apart, 2 ms attack, ~100 ms decay
"${F[@]}" -f lavfi -i "sine=f=660:d=0.12:r=48000" -f lavfi -i "sine=f=1320:d=0.09:r=48000" -filter_complex \
"[0]afade=t=in:d=0.002,afade=t=out:st=0.015:d=0.105:curve=exp,volume=0.8[a];[1]afade=t=in:d=0.001,afade=t=out:st=0.01:d=0.08:curve=exp,volume=0.4[b];\
[a][b]amix=inputs=2:duration=longest:normalize=0,highpass=f=250,lowpass=f=4500,acompressor=threshold=0.35:ratio=3:attack=1:release=60,volume=4.88" "${A[@]}" "$O/pop.wav"

# soft-pop: lower, rounder, shorter (list items)
"${F[@]}" -f lavfi -i "sine=f=520:d=0.09:r=48000" -f lavfi -i "sine=f=1040:d=0.06:r=48000" -filter_complex \
"[0]afade=t=in:d=0.003,afade=t=out:st=0.01:d=0.08:curve=exp,volume=0.8[a];[1]afade=t=in:d=0.002,afade=t=out:st=0.008:d=0.05:curve=exp,volume=0.25[b];\
[a][b]amix=inputs=2:duration=longest:normalize=0,highpass=f=200,lowpass=f=2800,volume=5.54" "${A[@]}" "$O/soft-pop.wav"

# tick: bright two-tone click (timers, counters)
"${F[@]}" -f lavfi -i "sine=f=1150:d=0.05:r=48000" -f lavfi -i "sine=f=2300:d=0.04:r=48000" -filter_complex \
"[0]afade=t=in:d=0.001,afade=t=out:st=0.004:d=0.045:curve=exp,volume=0.7[a];[1]afade=t=in:d=0.001,afade=t=out:st=0.003:d=0.035:curve=exp,volume=0.4[b];\
[a][b]amix=inputs=2:duration=longest:normalize=0,highpass=f=600,lowpass=f=6000,volume=5.31" "${A[@]}" "$O/tick.wav"

# typing-tick: a short noise click with a little tonal body (code typing)
"${F[@]}" -f lavfi -i "anoisesrc=color=white:d=0.035:r=48000:seed=7" -f lavfi -i "sine=f=1800:d=0.025:r=48000" -filter_complex \
"[0]highpass=f=2000,lowpass=f=7000,afade=t=in:d=0.001,afade=t=out:st=0.003:d=0.03:curve=exp,volume=0.9[a];[1]afade=t=in:d=0.001,afade=t=out:st=0.002:d=0.022:curve=exp,volume=0.35[b];\
[a][b]amix=inputs=2:duration=longest:normalize=0,volume=1.336" "${A[@]}" "$O/typing-tick.wav"

# whoosh: pink noise, band-limited, swell in then tail out (layout switches)
"${F[@]}" -f lavfi -i "anoisesrc=color=pink:d=0.45:r=48000:seed=11" -af \
"highpass=f=180,lowpass=f=2600,bandpass=f=900:width_type=o:w=2.2,afade=t=in:d=0.17:curve=qsin,afade=t=out:st=0.17:d=0.28:curve=exp,volume=2.636" "${A[@]}" "$O/whoosh.wav"

# stamp-thud: low sine body with fast exponential decay + a short dull noise slap
"${F[@]}" -f lavfi -i "aevalsrc='0.9*sin(2*PI*95*t)*exp(-18*t)+0.35*sin(2*PI*190*t)*exp(-28*t)':d=0.26:s=48000" -f lavfi -i "anoisesrc=color=brown:d=0.04:r=48000:seed=3" -filter_complex \
"[1]lowpass=f=1400,afade=t=out:st=0.005:d=0.035:curve=exp,volume=0.8[n];[0][n]amix=inputs=2:duration=longest:normalize=0,afade=t=in:d=0.001,afade=t=out:st=0.2:d=0.06,highpass=f=40,acompressor=threshold=0.4:ratio=4:attack=1:release=80,volume=1.256" "${A[@]}" "$O/stamp-thud.wav"

# pen-scratch: high pink-noise band with a fast flutter (underlines, highlights)
"${F[@]}" -f lavfi -i "anoisesrc=color=pink:d=0.22:r=48000:seed=5" -af \
"highpass=f=3000,lowpass=f=5500,tremolo=f=26:d=0.55,afade=t=in:d=0.02,afade=t=out:st=0.12:d=0.1,volume=3.94" "${A[@]}" "$O/pen-scratch.wav"

# riser: rising chirp (220 -> ~900 Hz) under a swelling noise bed, ends hard on the cut
"${F[@]}" -f lavfi -i "aevalsrc='0.35*sin(2*PI*(220*t+280*t*t))':d=1.2:s=48000" -f lavfi -i "anoisesrc=color=pink:d=1.2:r=48000:seed=9" -filter_complex \
"[1]highpass=f=400,lowpass=f=4000,volume=0.6[n];[0][n]amix=inputs=2:duration=longest:normalize=0,afade=t=in:d=1.12:curve=exp,afade=t=out:st=1.12:d=0.08,volume=1.494" "${A[@]}" "$O/riser.wav"

# sub-boom: 50/100 Hz sines with a slow exponential decay (dark punch moments)
"${F[@]}" -f lavfi -i "aevalsrc='0.85*sin(2*PI*50*t)*exp(-4*t)+0.35*sin(2*PI*100*t)*exp(-7*t)':d=0.9:s=48000" -af \
"afade=t=in:d=0.004,afade=t=out:st=0.75:d=0.15,highpass=f=25,volume=0.649" "${A[@]}" "$O/sub-boom.wav"
```

**Kit v2 (2026-11-20, `system-design-of-ai/11-max-tokens-and-truncation`): v1 + `bell.wav`.** Built into `~/.cache/video-toolkit/sfx/v2/` (v1 files copied unchanged, so v1 projects still match). Use it for an exam/time's-up bell (a hard limit hitting), at most a signature cue or two per video, ~9 dB under the voice peak:

```bash
# bell: hand-bell partials (1180 / 2360 / 3257 / 6372 Hz) with exponential decays and a 7 Hz shimmer, then calibrated to -3.0 dBFS peak
ffmpeg -hide_banner -loglevel error -y -f lavfi -i "aevalsrc='(0.6*sin(2*PI*1180*t)*exp(-3.2*t)+0.35*sin(2*PI*2360*t)*exp(-4.5*t)+0.28*sin(2*PI*3257*t)*exp(-6*t)+0.12*sin(2*PI*6372*t)*exp(-11*t))*(1+0.25*sin(2*PI*7*t))':d=1.4:s=48000" \
  -af "afade=t=in:d=0.002,afade=t=out:st=1.15:d=0.25,highpass=f=300,volume=0.7079" -ar 48000 -ac 1 -c:a pcm_s16le "$O/bell.wav"
```

Check after a build: 9 WAVs (v2: 10), 48 kHz mono, each peak −3.0 ±0.1 dBFS (`astats`), lengths as in the table. Save a tiled spectrogram sheet (`showspectrumpic` per file, `tile`) as `sheet.png` next to them.

**2 · Default event map.** Creative direction in `CLAUDE.md` may change it per video; the map below is the default.

| Visual event | Sound | Under voice peak |
|---|---|---|
| Layout switch HEAD ↔ FULL / SPLIT (brand wipe) | whoosh | 11 dB |
| Card or `FlowCard` entrance | pop | 10 dB |
| Items in `ChoicePills`, `Checklist` or any list | soft-pop, one per item, on the item's stagger | 13 dB |
| `Stamp` (and `Badge` / `KeyCard` stamp-ins) | stamp-thud | 10 dB |
| `Timer`, `CountdownKey`, `Counter` and other counters | tick, per step | 12 dB |
| Code typing (`CodeCard`, `TypingIntro`) | typing-tick about every 0.15 s across the typing span | 14 dB |
| `Highlight` or an underline | pen-scratch | 12 dB |
| Dark punch moment (HEAD/FULL dark style) | sub-boom, **max 2 per video** | 16 dB |
| A big cut into a new part | riser into the cut, then the cut's own hit on it | 16 dB |

Any other component: map it from `components/index.md` by what the viewer sees (something appears → pop, something moves across → whoosh, something is written → pen-scratch, something counts → tick, something lands hard → stamp-thud). A component spec that already names an SFX keeps its intent but uses the kit sound.

**3 · Timing**

- Each SFX **starts 2–3 frames before its visual lands** (the frame where the spring settles or the element reaches its place). Early reads as in sync; late reads as broken.
- Riser into a cut: it ends exactly on the cut frame, and the hit (whoosh or sub-boom) starts on the cut.
- Cues come from the same word-triggered events as the visuals (`timeline.json`, the `at()` lookups), never typed times. Export them to `work/audio/sfx_cues.json`: one entry per sound with `t` (seconds, output timeline), `visual_t` (the landing time it serves), `sound`, `gain_db` and `event` (a short label).
- Re-derive the cues for each composition: main and trailer 9:16, plus trailer 16:9 for long-form only (a reel has no 16:9 composition). A trailer that replays Main per segment maps each main cue through its segment offset and drops cues outside the kept ranges.

**4 · Density**

- One sound per beat hit, not one per element. A card with a title, three rows and an arrow gets one pop on the card, plus soft-pops only if the rows are a list I read out.
- A calm explanation beat may have no sound at all.
- Two sounds closer than ~120 ms collapse into one: keep the more important one.
- The closing recap and "Bye bye, sayonara!" get no sting.

**5 · Levels**

- `gain_db` = (voice peak in dBFS) − (dB under voice peak, from the map) + 3. Measure the voice peak on `work/audio/clean.wav` once (`astats` Peak level). That puts every SFX peak 10–16 dB under my voice's peaks; boom and riser are the quietest.
- Music bed: about −24 LUFS on its own, and it ducks a further 8–10 dB while I speak.

**6 · Music (optional, default none)**

- Look in this order: Pixabay Music, Freesound (CC0 filter), Mixkit, then Uppbeat. Pick by mood, tempo and a clean ending.
- Prefer licences that need no attribution (Pixabay Content License, CC0, Mixkit free licence). CC-BY only with the credit in `<name>_social.json` (every post that uses the video). Never NC or ND licences, never Instagram/TikTok in-app music, never commercial songs.
- Put the file in `projects/<name>/assets/music/` with a line in `assets/music/SOURCES.md`: URL, author, licence. If you can't download it, tell me which track (link, author, licence) and I'll drop it in.

**7 · Mix offline.** Remotion does no ducking, so the delivered audio is built with ffmpeg, not taken from the render.

The voice is always the Prep-verified cleaned voice (`pipeline/voice-cleaning.md`): `work/audio/clean.wav` is a copy of a verified `work/audio/cleaned/<recording-id>.wav`, and the cut voice is trimmed from it, from each recording's own cleaned WAV when there are several. Never re-extract voice from `raw/`, a proxy or the Remotion render. Don't add more denoise or dereverb here; the main mix and both trailer mixes use the same voice source.

1. **SFX track:** `work/audio/sfx.wav`, from `sfx_cues.json`: each cue's file through `adelay=<t in ms>:all=1` and `volume=<gain_db>dB`, all through `amix=inputs=N:normalize=0`, padded to the composition length (`apad=whole_dur=<s>`). A small per-project script in `work/scripts/` writes the filtergraph.
2. **Music (if any):** loop or trim to length (`aloop` / `atrim`, fade the last 1.5 s), set to about −24 LUFS with `volume`, then duck it with `sidechaincompress` keyed on the clean voice. Start at `threshold=0.02:ratio=2.5:attack=15:release=350` and adjust `ratio` until the measured duck in speech windows is 8–10 dB.
3. **Mix:** `amix=inputs=3:normalize=0` of `clean.wav` (laid out on the output timeline), `sfx.wav` and the ducked music → `work/audio/mix.wav`, 48 kHz.

`pipeline/render.md` muxes `mix.wav` (one per composition: `mix.wav`, `mix_trailer_9x16.wav`, and `mix_trailer_16x9.wav` for long-form only); the Remotion master's own audio isn't used. SFX `<Audio>` in the Remotion composition is for preview only.

**8 · Delegation**

- Building the kit and exporting `sfx_cues.json` from the decided map are low-stakes (chain in `pipeline/delegation.md`). Verify both yourself.
- The final mix runs with the render batch as a heavy job (detached Haiku runner).
- The sound map (which events sound, which sound, how loud) is creative: never delegate it.

**Checks**

- Every SFX onset is 1–3 frames before its visual trigger: `visual_t − t` in `sfx_cues.json`, and the first sample above −40 dBFS in `sfx.wav` after each `t`. List any that aren't.
- Music sits ≥ 15 dB under my voice during speech: measure the RMS of each stem (voice, ducked music) inside the speech windows from `timeline.json` (`atrim` + `astats`) and report the smallest gap.
- Save a spectrogram of the mix to `work/qa/mix_spectrum.png` and look at it (SFX spikes, music bed under the voice, no wideband clicks).
- Final loudness per `CLAUDE.md` → House numbers, checked in `qa.md`.

**Gotchas**

- A sound on every element turns into noise. One per beat hit; let calm beats breathe.
- An SFX that lands late reads as a sync bug, even when the picture is perfect. Lead the visual by 2–3 frames.
- A sine or decay that stops mid-cycle clicks: the first stamp-thud draft ended on a click at its last sample (a vertical line on the kit's spectrogram sheet). End every recipe with a fade.
- `amix` scales every input by 1/N unless `normalize=0`, so a 40-cue SFX track plays each sound 32 dB too quiet and the cue gains mean nothing. Always pass `normalize=0`.
- SFX sum on top of voice peaks: a −16 LUFS mix peaked at −0.4 dBFS on `system-design-of-ai/06-cancellation`, so a linear two-pass loudnorm couldn't stay linear. Put `alimiter=limit=0.69:level=false` (≈ −3.2 dBFS) before loudnorm in both the measure and apply passes (that project's `render_chain.sh`).
