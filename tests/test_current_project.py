"""A prompt that names no project is logged only into a project this session set."""
import os
import tempfile
import unittest

from tools.hooks import projlog


def make_root(td):
    with open(os.path.join(td, "CLAUDE.md"), "w") as f:
        f.write("rules\n")
    os.makedirs(os.path.join(td, "projects", "demo", "raw"))
    return os.path.join(td, "projects", "demo", "log.md")


def entries(log):
    if not os.path.isfile(log):
        return 0
    with open(log) as f:
        return f.read().count("**Prompt:**")


class CurrentProjectSessionTest(unittest.TestCase):
    def prompt(self, root, sid, text):
        projlog.cmd_prompt({"session_id": sid, "prompt": text}, root)

    def test_same_session_follow_up_is_logged(self):
        with tempfile.TemporaryDirectory() as td:
            log = make_root(td)
            self.prompt(td, "s1", "work on projects/demo")
            self.prompt(td, "s1", "now tighten the cut")
            self.assertEqual(entries(log), 2)
            self.assertEqual(projlog.read_current_project(td), ("projects/demo", "s1"))

    def test_new_session_does_not_inherit_the_project(self):
        with tempfile.TemporaryDirectory() as td:
            log = make_root(td)
            self.prompt(td, "s1", "work on projects/demo")
            self.prompt(td, "s2", "refactor the toolkit hooks")
            self.assertEqual(entries(log), 1)

    def test_legacy_file_without_session_is_not_used_for_logging(self):
        with tempfile.TemporaryDirectory() as td:
            log = make_root(td)
            with open(os.path.join(td, ".current-project"), "w") as f:
                f.write("projects/demo\n")
            self.prompt(td, "s1", "toolkit maintenance")
            self.assertEqual(entries(log), 0)

    def test_missing_session_id_never_matches(self):
        with tempfile.TemporaryDirectory() as td:
            log = make_root(td)
            projlog.cmd_prompt({"prompt": "work on projects/demo"}, td)
            projlog.cmd_prompt({"prompt": "something else"}, td)
            self.assertEqual(entries(log), 1)


if __name__ == "__main__":
    unittest.main()
