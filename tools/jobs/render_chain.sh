#!/bin/bash
# usage (from work/): tools/jobs/render_chain.sh [comp ...]   (default: every comp in the config, in order)
# Config (config/render_chain.json): {"outputs": {"<comp>": {"name": "<file without .mp4>", "mix": "audio/mix.wav"}}}
# Loudness targets are CLAUDE.md -> House numbers.
# ProRes master per comp -> mux with the offline mix (audio/mix*.wav, pipeline/sound.md) + 2-pass loudnorm -> out/
W="$PWD"; CFG="${RENDER_CONFIG:-$W/config/render_chain.json}"
[ -d "$W/remotion" ] || { echo "run from the project's work/ folder (no remotion/ here)" >&2; exit 2; }
ROWS=$(python3 -c 'import json,sys
for c, o in json.load(open(sys.argv[1]))["outputs"].items(): print(c, o["name"], o["mix"], sep="\t")' "$CFG") || { echo "bad config $CFG" >&2; exit 2; }
declare -A NAME MIX; ALL=()
while IFS=$'\t' read -r c name mix; do NAME[$c]=$name; case $mix in /*) MIX[$c]=$mix;; *) MIX[$c]="$W/$mix";; esac; ALL+=("$c"); done <<< "$ROWS"
OUT="$W/../out"; mkdir -p "$OUT" "$W/render" "$W/logs"; cd "$W/remotion"
COMPS=("$@"); [ ${#COMPS[@]} -eq 0 ] && COMPS=("${ALL[@]}")
for c in "${COMPS[@]}"; do [ -n "${NAME[$c]:-}" ] || { echo "comp $c is not in $CFG" >&2; exit 2; }; done
fail=0
for c in "${COMPS[@]}"; do
  echo "=== $c render start $(date +%T)"
  timeout 3600 gpu-run npx remotion render src/index.ts "$c" "$W/render/$c.mov" --codec=prores --prores-profile=standard --gl=angle --concurrency=3 --offthreadvideo-cache-size-in-bytes=2000000000 --timeout=120000 --muted > "$W/logs/render-$c.log" 2>&1
  rc=$?; echo "EXIT render $c $rc $(date +%T)"; [ $rc -ne 0 ] && { fail=1; continue; }
  A="${MIX[$c]}"
  M=$(ffmpeg -hide_banner -nostats -i "$A" -af alimiter=limit=0.69:level=false,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
  LN="alimiter=limit=0.69:level=false,loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000"
  timeout 1800 gpu-run ffmpeg -hide_banner -nostats -y -i "$W/render/$c.mov" -i "$A" -map 0:v -map 1:a -af "$LN" -c:v h264_nvenc -preset p6 -tune hq -rc vbr -cq 19 -b:v 0 -maxrate 20M -profile:v high -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ac 2 -shortest -movflags +faststart "$OUT/${NAME[$c]}.mp4" >> "$W/logs/render-$c.log" 2>&1
  rc=$?; echo "EXIT encode $c $rc $(date +%T)"; [ $rc -ne 0 ] && fail=1
  ffmpeg -hide_banner -nostats -i "$OUT/${NAME[$c]}.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" | tr -s ' ' | tr '\n' ' '; echo
  ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames -of compact "$OUT/${NAME[$c]}.mp4"
  ffmpeg -v error -i "$OUT/${NAME[$c]}.mp4" -f null - 2>&1 | head -3; echo "DECODE_CHECK $c done"
done
echo EXIT_CHAIN
exit $fail
