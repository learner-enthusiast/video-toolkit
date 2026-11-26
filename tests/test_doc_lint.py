"""Doc lint: catches config drift in the toolkit's markdown (tracked and new, non-ignored files)."""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# A line that lost its head: starts with ", " or with one space then a capital or a backtick.
ORPHAN = re.compile(r"^(, | [A-Z`])")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")

REQUIRED_PHRASES = ("Never cut any script line", "stop and ask me")
CUT_SKILLS = (".claude/skills/reel/SKILL.md", ".claude/skills/coding-video/SKILL.md")

NO_SHORT_REEL = (".claude/skills/reel/SKILL.md", "templates/script-reel.md")
SHORT_REEL = re.compile(r"30\s*[–-]\s*60 ?s\b")
OLD_PACE = re.compile(r"140\s*wpm", re.I)
# -14 next to LUFS in any order, or the old "-14 to -16" range.
OLD_LOUDNESS = re.compile(
    r"LUFS.*(?<![\w.])[−-]14(?:\.0)?(?![\d.])"
    r"|(?<![\w.])[−-]14(?:\.0)?\s*(?:LUFS|to\s*[−-]16)"
)
# Shapes that put the greeting before the hook.
GREETING_FIRST = (
    re.compile(r'Namoshkar!.*\bthen\b.*\bhook', re.I),
    re.compile(r'\b(?:open|opens|start|starts) with\s+(?:a\s+)?["“]?Namoshkar', re.I),
    re.compile(r'^\*\*(?:Spoken:|O1)\*\*[^"]*"Namoshkar'),
)

PATH_PREFIXES = ("pipeline/", "components/", "tools/", "templates/", "config/", ".claude/")
# Documented as per-project, so they don't exist in the toolkit.
PER_PROJECT_PREFIXES = ("work/", "projects/")
PLACEHOLDER = re.compile(r"[<>*{}$…|]")


def md_files():
    out = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "*.md"],
        cwd=ROOT,
    ).decode()
    for rel in sorted(set(filter(None, out.split("\0")))):
        parts = Path(rel).parts
        if parts[0] == "docs" or "references" in parts or not (ROOT / rel).is_file():
            continue
        yield rel


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def orphan_lines(text):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = FENCE.match(line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
        elif fence is None and ORPHAN.match(line):
            yield number, line


def repo_paths(text):
    for span in re.findall(r"`([^`\n]+)`", text):
        for token in span.split():
            token = token.strip("\"'(),;").rstrip(".:")
            token = re.split(r"#|:\d", token)[0]
            if token.startswith(PER_PROJECT_PREFIXES) or PLACEHOLDER.search(token):
                continue
            if token.startswith(PATH_PREFIXES):
                yield token


def matches(files, predicate):
    return [
        f"{rel}:{number}: {line[:120]}"
        for rel in files
        for number, line in enumerate(read(rel).splitlines(), 1)
        if predicate(line)
    ]


def skills_and_templates():
    return [
        rel for rel in md_files()
        if rel.startswith("templates/")
        or (rel.startswith(".claude/skills/") and rel.endswith("/SKILL.md"))
    ]


class DocLintTest(unittest.TestCase):
    def test_no_orphaned_fragments(self):
        bad = [f"{rel}:{n}: {line[:120]}" for rel in md_files() for n, line in orphan_lines(read(rel))]
        self.assertEqual(bad, [])

    def test_cut_skills_keep_the_hard_rules(self):
        for rel in CUT_SKILLS:
            for phrase in REQUIRED_PHRASES:
                with self.subTest(file=rel, phrase=phrase):
                    self.assertIn(phrase, read(rel))

    def test_no_short_reel_target(self):
        self.assertEqual(matches(NO_SHORT_REEL, SHORT_REEL.search), [])

    def test_no_old_pace(self):
        self.assertEqual(matches(md_files(), OLD_PACE.search), [])

    def test_no_old_loudness(self):
        self.assertEqual(matches(md_files(), OLD_LOUDNESS.search), [])

    def test_hook_comes_before_greeting(self):
        bad = matches(skills_and_templates(), lambda line: any(p.search(line) for p in GREETING_FIRST))
        self.assertEqual(bad, [])

    def test_backticked_repo_paths_exist(self):
        bad = sorted({
            f"{rel}: {path}"
            for rel in md_files() for path in repo_paths(read(rel))
            if not (ROOT / path).exists()
        })
        self.assertEqual(bad, [])


class DocLintRuleTest(unittest.TestCase):
    """The rules themselves, on known good and bad lines."""

    def test_orphan_rule(self):
        text = ", lost head\n Always lost\n `x` lost\n  Indented continuation\n```\n Fenced\n```\n- ok"
        self.assertEqual([n for n, _ in orphan_lines(text)], [1, 2, 3])

    def test_loudness_rule(self):
        for bad in ("at -14 to -16 LUFS", "to a reel's −14 LUFS / TP −1", "−16 LUFS (may say −14)", "-14.0 LUFS"):
            self.assertTrue(OLD_LOUDNESS.search(bad), bad)
        for good in ("−16 ± 0.5 LUFS", "duck at -14 dB", "dated 2026-11-14, LUFS"):
            self.assertFalse(OLD_LOUDNESS.search(good), good)

    def test_greeting_rule(self):
        for bad in (
            'Open with "Namoshkar!" (~1.5 s), then the hook line',
            'every script starts with "Namoshkar!"',
            '**Spoken:** "Namoshkar!" then "<hook line>"',
        ):
            self.assertTrue(any(p.search(bad) for p in GREETING_FIRST), bad)
        good = '**Spoken:** "<hook line>" (lands within 3 s), then "Namoshkar!"'
        self.assertFalse(any(p.search(good) for p in GREETING_FIRST))

    def test_path_rule(self):
        text = "`vt-python tools/x.py a` `pipeline/qa.md:12` `work/a.json` `components/specs/<Name>.md`"
        self.assertEqual(list(repo_paths(text)), ["tools/x.py", "pipeline/qa.md"])


if __name__ == "__main__":
    unittest.main()
