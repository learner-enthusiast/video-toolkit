#!/bin/bash
# Deliver QA: decode check + video-inspect (--thorough on the first video) + 5 s contact sheets. Run from work/.
# usage: tools/qa/qa_inspect.sh <main.mp4> [<trailer.mp4> ...]
set -o pipefail
[ $# -ge 1 ] || { echo "usage: qa_inspect.sh <main.mp4> [<trailer.mp4> ...]" >&2; exit 2; }
TOOLS="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p logs; rc=0
gpufree(){ for k in $(seq 1 900); do [ "$(nvidia-smi --query-compute-apps=process_name --format=csv,noheader | grep -c 'python\|chrome\|node')" = "0" ] && break; sleep 1; done; }
i=0
for F in "$@"; do
  V=$(basename "${F%.*}"); i=$((i+1))
  ffmpeg -v error -i "$F" -f null - 2>&1 | head -3; echo "EXIT decode $V ${PIPESTATUS[0]}"
  curl -s localhost:11434/api/generate -d '{"model":"qwen2.5vl:3b","keep_alive":0}' > /dev/null; sleep 4; gpufree
  TH=""; [ $i = 1 ] && TH="--thorough"
  echo "=== inspect $V $(date +%T)"
  gpu-run vt-python "$TOOLS/inspect/video_inspect.py" "$F" $TH > logs/inspect-$V.log 2>&1; r=$?; echo "EXIT inspect $V $r $(date +%T)"; [ $r = 0 ] || rc=$r
  D=inspect/$V; mkdir -p "$D"; rm -f "$D"/sheet_*.jpg
  if [[ "$V" == *_trailer_16x9 ]]; then SC="scale=480:-2,drawtext=text='%{pts\:hms}':x=6:y=h-th-8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,tile=4x3"; else SC="scale=360:-2,drawtext=text='%{pts\:hms}':x=6:y=h-th-8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,tile=6x2"; fi
  ffmpeg -hide_banner -v error -y -i "$F" -vf "fps=1/5,$SC" "$D/sheet_%02d.jpg"; echo "EXIT sheets $V $?"
done
exit $rc
