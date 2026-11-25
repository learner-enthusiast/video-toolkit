import json
import os
import tempfile
import unittest

from tools.project_state import (
    APPROVALS,
    authoritative_approvals,
    default_state,
    parse_approvals_from_log,
    parse_last_handoff,
    reconcile,
    save_state,
    sync_handoff,
)


class ProjectStateTest(unittest.TestCase):
    def test_default_state_schema(self):
        st = default_state("projects/demo")
        self.assertEqual(st["schema_version"], 1)
        self.assertIn("approval_evidence", st)

    def test_parse_explicit_approval(self):
        text = "foo\n**Approval:** rough_cut=approved\n"
        p = parse_approvals_from_log(text)
        self.assertEqual(p["rough_cut"]["value"], "approved")

    def test_newest_approval_wins(self):
        text = "**Approval:** rough_cut=rejected\n\n**Approval:** rough_cut=approved\n"
        p = parse_approvals_from_log(text)
        self.assertEqual(p["rough_cut"]["value"], "approved")

    def test_no_approval_unverified(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            open(os.path.join(proj, "log.md"), "w").write("# log\n")
            auth = authoritative_approvals(proj)
            self.assertFalse(auth["approvals"]["rough_cut"]["approved"])
            self.assertEqual(auth["approvals"]["rough_cut"]["status"], "unverified")

    def test_sync_does_not_infer_approval_from_stage(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            save_state(proj, default_state(proj))
            with open(os.path.join(proj, "log.md"), "w") as f:
                f.write("### Handoff: 3 · Compose\n**Next:** build storyboard\n")
            st = sync_handoff(proj)
            self.assertFalse(st["approvals"]["rough_cut"])

    def test_sync_mirrors_log_approval(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            save_state(proj, default_state(proj))
            with open(os.path.join(proj, "log.md"), "w") as f:
                f.write("**Approval:** rough_cut=approved\n### Handoff: 3 · Compose\n")
            st = sync_handoff(proj)
            self.assertTrue(st["approvals"]["rough_cut"])

    def test_reconcile_detects_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            st = default_state(proj)
            st["approvals"]["rough_cut"] = True
            save_state(proj, st)
            with open(os.path.join(proj, "log.md"), "w") as f:
                f.write("**Approval:** rough_cut=rejected\n")
            rec = reconcile(proj)
            self.assertTrue(any(i.get("approval") == "rough_cut" for i in rec["issues"]))

    def test_malformed_state_schema(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            with open(os.path.join(proj, "project-state.json"), "w") as f:
                f.write("{not json")
            from tools.validate.vt_validate import check_state_schema

            errs = check_state_schema(proj)
            self.assertTrue(any(e["code"] == "INVALID_STATE_SCHEMA" for e in errs))


if __name__ == "__main__":
    unittest.main()