#!/bin/bash
# Build the sound kit (pipeline/sound.md). usage: tools/sound/build_kit.sh <out-dir>
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

# Gain 0.5132 gives the stated -3.0 dBFS peak. The installed v2 bell.wav came from an unsaved recipe: same
# level and length, different samples. Never rebuild v2 over it.
# bell: hand-bell partials (1180 / 2360 / 3257 / 6372 Hz) with exponential decays and a 7 Hz shimmer, then calibrated to -3.0 dBFS peak
"${F[@]}" -f lavfi -i "aevalsrc='(0.6*sin(2*PI*1180*t)*exp(-3.2*t)+0.35*sin(2*PI*2360*t)*exp(-4.5*t)+0.28*sin(2*PI*3257*t)*exp(-6*t)+0.12*sin(2*PI*6372*t)*exp(-11*t))*(1+0.25*sin(2*PI*7*t))':d=1.4:s=48000" \
  -af "afade=t=in:d=0.002,afade=t=out:st=1.15:d=0.25,highpass=f=300,volume=0.5132" -ar 48000 -ac 1 -c:a pcm_s16le "$O/bell.wav"
