#!/usr/bin/env python3
"""Save the Hindi script from an editing prompt as the twin's script.md. A file write, nothing else.

usage: vt-python tools/twin/save_hindi_script.py projects/<name> <prompt.md> [--force]
Takes the `# Hindi script` section (with `## Hindi 60-second cut`) of an English prompt, or the
`# Script (Hindi, romanized)` section of a Hindi prompt. Exit 3: the prompt has none.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.script_beats import id_problems, parse_beats  # noqa: E402
from tools.twin import common  # noqa: E402

HEAD = re.compile(r"^#\s+(Hindi script\b.*|Script\s*\(Hindi.*)$", re.I)
OWN_SUB = re.compile(r"^##\s+(Hindi\s+)?60-second cut\b", re.I)


def extract(prompt: str) -> str | None:
    lines = prompt.splitlines()
    start = next((i for i, line in enumerate(lines) if HEAD.match(line)), None)
    if start is None:
        return None
    out = [lines[start]]
    for line in lines[start + 1:]:
        if re.match(r"^#\s", line):
            break
        # an English prompt's own `## 60-second cut` after the Hindi block is not ours
        if re.match(r"^##\s+60-second cut\b", line, re.I) and "Hindi script" in lines[start]:
            break
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("english")
    ap.add_argument("prompt")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    with open(args.prompt, encoding="utf-8") as f:
        script = extract(f.read())
    if script is None:
        print("no Hindi script section in this prompt")
        return 3
    ids = [b["id"] for b in parse_beats(script)]
    problems = id_problems(ids) or ([] if ids and ids[0] else ["no beat IDs ([B01 | HEAD] ...)"])
    if problems:
        print("; ".join(problems), file=sys.stderr)
        return 1
    path = os.path.join(common.twin_path(args.english), "script.md")
    if os.path.exists(path) and not args.force:
        with open(path, encoding="utf-8") as f:
            if f.read() == script:
                print(f"{path}: already saved")
                return 0
        print(f"{path} exists and differs; use --force to replace it", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(script)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
