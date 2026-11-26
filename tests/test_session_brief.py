import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOK = os.path.join(REPO, "tools", "hooks", "session_brief.py")
LOG = """# Log: demo

### Handoff: 1 · Prep → 2 · Cut
**Open issues:** old issue

## 2026-01-02 · cut

**Approval:** rough_cut=approved

### Handoff (Cut complete)
**Open issues:** line 14 needs a re-record
**Next:** Compose

## 2026-01-03 · a later entry that is not part of the handoff
"""


def make_root(td, log=LOG, current="projects/demo\nsid-1\n", state=None):
    with open(os.path.join(td, "CLAUDE.md"), "w") as f:
        f.write("rules\n")
    project = os.path.join(td, "projects", "demo")
    os.makedirs(project)
    if log is not None:
        with open(os.path.join(project, "log.md"), "w") as f:
            f.write(log)
    if current is not None:
        with open(os.path.join(td, ".current-project"), "w") as f:
            f.write(current)
    if state is not None:
        with open(os.path.join(project, "project-state.json"), "w") as f:
            f.write(state)


def run_hook(td, stdin='{"source": "startup"}'):
    return subprocess.run(
        [sys.executable, HOOK], input=stdin, capture_output=True, text=True, timeout=20,
        env={**os.environ, "CLAUDE_PROJECT_DIR": td},
    )


class SessionBriefTest(unittest.TestCase):
    def check_silent(self, result):
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_no_current_project_is_silent(self):
        with tempfile.TemporaryDirectory() as td:
            make_root(td, current=None)
            self.check_silent(run_hook(td))

    def test_unknown_project_is_silent(self):
        with tempfile.TemporaryDirectory() as td:
            make_root(td, current="projects/gone\n")
            self.check_silent(run_hook(td))

    def test_valid_project(self):
        state = json.dumps({
            "schema_version": 1, "stage": "compose", "status": "in_progress",
            "approvals": {k: False for k in ("script", "rough_cut", "storyboard", "stills", "final")},
            "next_actions": ["storyboard"], "open_issues": [],
        })
        with tempfile.TemporaryDirectory() as td:
            make_root(td, state=state)
            out = run_hook(td).stdout
        self.assertIn("# Session brief: projects/demo", out)
        self.assertIn("stage=compose", out)
        self.assertIn("rough_cut=approved", out)
        self.assertIn("line 14 needs a re-record", out)
        self.assertNotIn("old issue", out)
        self.assertNotIn("a later entry", out)

    def test_project_without_state_file_still_briefs(self):
        with tempfile.TemporaryDirectory() as td:
            make_root(td, current="projects/demo\n")  # old one-line .current-project
            out = run_hook(td).stdout
        self.assertIn("no project-state.json", out)
        self.assertIn("### Handoff (Cut complete)", out)

    def test_oversized_handoff_is_capped_with_pointer(self):
        big = LOG.replace("**Next:** Compose", "**Next:** Compose\n" + "- ₹ detail line\n" * 800)
        with tempfile.TemporaryDirectory() as td:
            make_root(td, log=big)
            out = run_hook(td).stdout
        self.assertLessEqual(len(out.encode()), 4096)
        self.assertRegex(out, r"truncated; read projects/demo/log\.md from line \d+")

    def test_corrupt_state_is_silent(self):
        for state in ("{not json", '{"schema_version": 99}'):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as td:
                make_root(td, state=state)
                self.check_silent(run_hook(td))
                # The hook is read-only: it must not quarantine or rewrite anything.
                with open(os.path.join(td, "projects", "demo", "project-state.json")) as f:
                    self.assertEqual(f.read(), state)

    def test_bad_stdin_is_silent(self):
        with tempfile.TemporaryDirectory() as td:
            make_root(td)
            self.check_silent(run_hook(td, stdin="garbage"))


if __name__ == "__main__":
    unittest.main()
