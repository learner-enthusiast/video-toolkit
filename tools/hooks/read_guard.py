#!/usr/bin/env python3
"""PreToolUse hook for the Read tool: refuse files that must never be loaded whole.

A permissions `deny` Read rule can't do this: Claude Code also applies it to Bash
commands that name the file (tested on 2.1.332: it blocked the prescribed
`grep ... icons/icons.md`, `cp` out of raw/ and `ls raw/`). This hook only sees the
Read tool, so shell lookups and media tools keep working. Fails open.
"""
import fnmatch
import json
import os
import sys

# A ranged Read this small is allowed on the two lookup tables (Edit needs a prior Read).
RANGED_OK = ("icons/icons.md", "components/index-full.md")
MAX_RANGE = 40

# Matched against the path relative to the toolkit root; `*` also crosses `/`.
BLOCKED = (
    ("icons/icons.md", "use bash: grep -i '<brand>' icons/icons.md"),
    ("components/index-full.md", "use bash: grep -i '^| \\[<Name>\\]' components/index-full.md"),
    ("projects/*/raw/*", "originals are never read; probe with ffprobe, work on copies in work/"),
    ("node_modules/*", "use bash grep for the one symbol you need"),
    ("*/node_modules/*", "use bash grep for the one symbol you need"),
    ("*.mp4", "binary media: use ffprobe or video-inspect"),
    ("*.mov", "binary media: use ffprobe or video-inspect"),
    ("*.wav", "binary media: use ffprobe or the cleaning report"),
)


def blocked_reason(file_path: str, root: str, limit=None) -> str | None:
    root = os.path.realpath(root)
    # Check the path as given and with symlinks resolved.
    for path in (os.path.abspath(os.path.join(root, file_path)),
                 os.path.realpath(os.path.join(root, file_path))):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        for pattern, why in BLOCKED:
            if fnmatch.fnmatchcase(rel.lower() if pattern.startswith("*.") else rel, pattern):
                if rel in RANGED_OK and isinstance(limit, int) and 0 < limit <= MAX_RANGE:
                    continue
                return why
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Read":
            return 0
        root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
        args = data.get("tool_input") or {}
        path = args.get("file_path") or ""
        why = blocked_reason(path, root, args.get("limit")) if path else None
    except Exception:
        return 0
    if why:
        sys.stderr.write(f"Blocked by tools/hooks/read_guard.py: don't Read this file; {why}\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
