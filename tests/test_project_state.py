import json
import os
import tempfile
import unittest

from tools.project_state import (
    default_state,
    parse_last_handoff,
    save_state,
    state_path,
    sync_handoff,
)


class ProjectStateTest(unittest.TestCase):
    def test_default_state_schema(self):
        st = default_state("projects/demo")
        self.assertEqual(st["schema_version"], 1)
        self.assertEqual(st["master_language"], "en")
        self.assertIn("rough_cut", st["approvals"])

    def test_parse_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            log = os.path.join(td, "log.md")
            with open(log, "w") as f:
                f.write(
                    "### Handoff: 2 · Cut → 3 · Compose\n"
                    "**Decisions:** take 2\n"
                    "**Open issues:** none\n"
                    "**Next:** build storyboard\n"
                )
            h = parse_last_handoff(log)
            self.assertIn("Cut", h["stage_line"])

    def test_sync_sets_compose_approval(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "projects", "x")
            os.makedirs(proj)
            save_state(proj, default_state(proj))
            with open(os.path.join(proj, "log.md"), "w") as f:
                f.write(
                    "### Handoff: 3 · Compose\n"
                    "**Next:** start composition\n"
                )
            st = sync_handoff(proj)
            self.assertTrue(st["approvals"]["rough_cut"])
            self.assertEqual(st["stage"], "compose")


if __name__ == "__main__":
    unittest.main()