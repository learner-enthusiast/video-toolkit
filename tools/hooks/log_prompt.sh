#!/usr/bin/env bash
# UserPromptSubmit hook: save the prompt to projects/<name>/work/prompts/ and
# write the log.md entry header (pipeline/project-log.md). Silent, always exit 0.
python3 "$(dirname "$0")/projlog.py" prompt >/dev/null 2>&1
exit 0
