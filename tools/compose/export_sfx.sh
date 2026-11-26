#!/usr/bin/env bash
# SFX cue times from the composition's sound map, then the offline mixes (pipeline/sound.md §7).
# usage (from work/): tools/compose/export_sfx.sh      needs remotion/scripts/export_cues.ts (imports src/plan)
# --preserve-symlinks: in a Hindi twin, src/ links to the English code and must read the twin's data.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p audio scripts
(cd remotion && npx esbuild scripts/export_cues.ts --bundle --platform=node --loader:.json=json --preserve-symlinks \
  --log-level=warning --outfile=../scripts/.export_cues.cjs)
node scripts/.export_cues.cjs audio
for which in main trailer; do
  vt-python "$HERE/mix.py" "$which"        # lays the voice stem out and mixes voice + SFX
  rc=0; vt-python "$HERE/../sound/music_bed.py" "$which" || rc=$?
  case $rc in
    0) vt-python "$HERE/mix.py" "$which" --music "audio/stems/$which-music.wav" ;;
    3) ;;                                  # this video has no music bed
    *) exit "$rc" ;;
  esac
done
