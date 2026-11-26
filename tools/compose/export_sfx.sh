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
vt-python "$HERE/mix.py" main
vt-python "$HERE/mix.py" trailer
