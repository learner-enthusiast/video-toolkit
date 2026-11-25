import json
import os
import tempfile
import unittest
from unittest import mock

from tools.validate import vt_validate


class ValidateTest(unittest.TestCase):
    def _project(self, log_body=""):
        td = tempfile.mkdtemp()
        proj = os.path.join(td, "p")
        for d in ("raw", "work", "out"):
            os.makedirs(os.path.join(proj, d))
        with open(os.path.join(proj, "script.md"), "w") as f:
            f.write("# s\n")
        with open(os.path.join(proj, "log.md"), "w") as f:
            f.write(log_body)
        state = {
            "schema_version": 1,
            "stage": "compose",
            "approvals": {k: False for k in ["script", "rough_cut", "storyboard", "stills", "final"]},
        }
        with open(os.path.join(proj, "project-state.json"), "w") as f:
            json.dump(state, f)
        return proj

    def test_project_missing_script(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(os.path.join(proj, "raw"))
            os.makedirs(os.path.join(proj, "work"))
            os.makedirs(os.path.join(proj, "out"))
            errs = vt_validate.check_project(proj)
            self.assertTrue(any(e["code"] == "MISSING_FILE" for e in errs))

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
        proj = self._project("# log\n")
        errs = vt_validate.check_stage(proj)
        codes = {e["code"] for e in errs}
        self.assertIn("APPROVAL_UNVERIFIABLE", codes)

    def test_stage_with_approval(self):
        proj = self._project("**Approval:** rough_cut=approved\n")
        errs = vt_validate.check_stage(proj)
        self.assertFalse(any(e["code"] == "ROUGH_CUT_NOT_APPROVED" for e in errs))

    def test_state_out_of_sync(self):
        proj = self._project("**Approval:** rough_cut=rejected\n")
        with open(os.path.join(proj, "project-state.json")) as f:
            st = json.load(f)
        st["approvals"]["rough_cut"] = True
        with open(os.path.join(proj, "project-state.json"), "w") as f:
            json.dump(st, f)
        errs = vt_validate.check_stage(proj)
        self.assertTrue(any(e["code"] == "STATE_OUT_OF_SYNC" for e in errs))

    def test_stage_malformed_json_no_crash(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            for d in ("raw", "work", "out"):
                os.makedirs(os.path.join(proj, d))
            with open(os.path.join(proj, "script.md"), "w") as sf:
                sf.write("# s\n")
            with open(os.path.join(proj, "log.md"), "w") as lf:
                lf.write("**Approval:** rough_cut=approved\n")
            with open(os.path.join(proj, "project-state.json"), "w") as f:
                f.write("[1,2,3]")
            errs = vt_validate.check_stage(proj)
            codes = {e["code"] for e in errs}
            self.assertIn("INVALID_STATE_SCHEMA", codes)

    def test_parse_frame_rate_rational(self):
        self.assertAlmostEqual(vt_validate.parse_frame_rate("30000/1001"), 29.97002997002997)
        self.assertAlmostEqual(vt_validate.parse_frame_rate("30/1"), 30.0)
        self.assertIsNone(vt_validate.parse_frame_rate("0/0"))

    def test_measure_loudness_skipped_without_expectation(self):
        errs, lufs, peak = vt_validate.measure_loudness("dummy.mp4", {})
        self.assertEqual(errs, [])
        self.assertIsNone(lufs)
        self.assertIsNone(peak)

    def test_check_render_mocked(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as vf:
            vf.write(b"\x00" * 512)
            path = vf.name
        probe = {
            "format": {"duration": "10.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30000/1001",
                    "pix_fmt": "yuv420p",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "sample_rate": "48000",
                    "channels": 2,
                },
            ],
        }
        try:
            with mock.patch.object(vt_validate, "ffprobe_json", return_value=probe):
                with mock.patch.object(vt_validate, "ffmpeg_full_decode"):
                    with mock.patch.object(
                        vt_validate,
                        "measure_loudness",
                        return_value=([], -16.0, -2.0),
                    ):
                        errs = vt_validate.check_render(
                            path,
                            {
                                "width": 1920,
                                "height": 1080,
                                "fps": 29.97,
                                "pixel_format": "yuv420p",
                                "audio_codec": "aac",
                                "sample_rate": 48000,
                                "channels": 2,
                                "lufs_target": -16,
                            },
                        )
            self.assertEqual(errs, [])
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()