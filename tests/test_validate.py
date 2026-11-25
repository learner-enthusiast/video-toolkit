import json
import os
import tempfile
import unittest

from tools.validate import vt_validate


class ValidateTest(unittest.TestCase):
    def test_project_missing_script(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(os.path.join(proj, "raw"))
            os.makedirs(os.path.join(proj, "work"))
            os.makedirs(os.path.join(proj, "out"))
            errs = vt_validate.check_project(proj)
            codes = {e["code"] for e in errs}
            self.assertIn("MISSING_FILE", codes)

    def test_srt_overlap(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
            f.write(
                "1\n00:00:00,000 --> 00:00:02,000\nHi\n\n"
                "2\n00:00:01,500 --> 00:00:03,000\nThere\n"
            )
            path = f.name
        try:
            errs = vt_validate.check_subtitles(path)
            self.assertTrue(any(e["code"] == "SRT_OVERLAP" for e in errs))
        finally:
            os.remove(path)

    def test_stage_compose_without_approval(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            state = {
                "schema_version": 1,
                "stage": "compose",
                "approvals": {"rough_cut": False},
            }
            with open(os.path.join(proj, "project-state.json"), "w") as f:
                json.dump(state, f)
            errs = vt_validate.check_stage(proj)
            self.assertTrue(any(e["code"] == "ROUGH_CUT_NOT_APPROVED" for e in errs))


if __name__ == "__main__":
    unittest.main()