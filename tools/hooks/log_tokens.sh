#!/usr/bin/env bash
# Stop hook: append Finished / Took / Tokens (main + subagents) under the
# turn's log.md entry. The transcript scan runs detached so the hook returns
# at once. Silent, always exit 0.
input=$(cat)
if [ "${PROJLOG_FOREGROUND:-0}" = "1" ]; then
  printf '%s' "$input" | python3 "$(dirname "$0")/projlog.py" tokens >/dev/null 2>&1
else
  printf '%s' "$input" | setsid nohup python3 "$(dirname "$0")/projlog.py" tokens >/dev/null 2>&1 &
fi
exit 0
