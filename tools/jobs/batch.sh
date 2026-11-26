#!/usr/bin/env bash
# Deterministic heavy-job runner (pipeline/delegation.md, Heavy jobs).
# usage: tools/jobs/batch.sh projects/<name>/work/jobs/<name>.batch
# One job per line, `#` comments allowed:
#   NN-name | timeout-seconds | output-path | command (bash; may contain pipes)
# Jobs run strictly one at a time, in file order, from the work/ folder (the parent of the batch
# file's folder), through run.sh. The batch stops at the first failed or timed-out job.
# Exit: 0 all done · 1 a job failed · 2 bad batch file (nothing ran) · 3 another batch is running.
set -u
FILE=${1:-}
[ -f "$FILE" ] || { echo "usage: batch.sh <batch-file>" >&2; exit 2; }
JOBS=$(cd "$(dirname "$FILE")" && pwd); WORK=$(dirname "$JOBS")
RUN="$(cd "$(dirname "$0")" && pwd)/run.sh"
trim() { local s=$1; s="${s#"${s%%[![:space:]]*}"}"; printf '%s' "${s%"${s##*[![:space:]]}"}"; }

# Parse and check the whole file before running anything.
ids=(); limits=(); outputs=(); commands=(); n=0; declare -A seen
while IFS= read -r line || [ -n "$line" ]; do
  n=$((n+1)); line=$(trim "$line")
  [ -z "$line" ] && continue
  [[ $line == \#* ]] && continue
  IFS='|' read -r id limit output command <<< "$line"
  id=$(trim "$id"); limit=$(trim "${limit:-}"); output=$(trim "${output:-}"); command=$(trim "${command:-}")
  if ! [[ $id =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ && $limit =~ ^[1-9][0-9]*$ ]] || [ -z "$output" ] || [ -z "$command" ]; then
    echo "batch.sh: line $n: expected 'id | timeout | output | command'" >&2; exit 2
  fi
  [ -z "${seen[$id]:-}" ] || { echo "batch.sh: line $n: duplicate job id $id" >&2; exit 2; }
  seen[$id]=1; ids+=("$id"); limits+=("$limit"); outputs+=("$output"); commands+=("$command")
done < "$FILE"
[ ${#ids[@]} -gt 0 ] || { echo "batch.sh: no jobs in $FILE" >&2; exit 2; }

exec 9> "$JOBS/.batch.lock"
flock -n 9 || { echo "batch.sh: another batch is running in $JOBS" >&2; exit 3; }

# Stale results from an earlier run must not read as this run's.
for id in "${ids[@]}"; do rm -f "$JOBS/$id.status" "$JOBS/$id.status.tmp" "$JOBS/$id.log"; done

for i in "${!ids[@]}"; do
  id=${ids[$i]}
  echo "START $id ($((i+1))/${#ids[@]}) $(date +%T)"
  # 9>&-: a job must not inherit the lock.
  (cd "$WORK" && JOBS_DIR="$JOBS" bash "$RUN" "$id" "${limits[$i]}" "${outputs[$i]}" -- bash -c "set -o pipefail; ${commands[$i]}" 9>&-)
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "BATCH FAILED at $id exit=$rc (status: $JOBS/$id.status); $(( ${#ids[@]} - i - 1 )) job(s) not run"
    exit 1
  fi
  echo "DONE $id $(date +%T)"
done
echo "BATCH DONE ${#ids[@]} job(s)"
