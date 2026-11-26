#!/bin/bash
# usage: tools/jobs/run.sh <NN-job> <timeout-seconds> <output-path> -- <command...>
# Writes <jobs>/<NN-job>.log and, only when the job ends (atomic mv), <jobs>/<NN-job>.status.
# <jobs> is $JOBS_DIR, else ./jobs (run from the project's work/ folder). Exit code = the command's.
N=$1; T=$2; OUT=$3; shift 4; D="${JOBS_DIR:-$PWD/jobs}"; mkdir -p "$D"
t0=$(date +%s); timeout "$T" "$@" > "$D/$N.log" 2>&1; rc=$?
{ echo "state=$([ $rc = 0 ] && echo done || echo failed)"; echo "exit=$rc"
  echo "seconds=$(( $(date +%s) - t0 ))"; echo "output=$OUT"; echo "log_tail<<"; tail -20 "$D/$N.log"
} > "$D/$N.status.tmp" && mv "$D/$N.status.tmp" "$D/$N.status"
exit $rc
