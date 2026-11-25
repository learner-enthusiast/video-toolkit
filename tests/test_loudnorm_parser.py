import os
import subprocess
import tempfile
import unittest
from unittest import mock

from tools.validate import vt_validate


FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "loudnorm_multiline_stderr.txt")


class LoudnormParserTest(unittest.TestCase):
    def setUp(self):
        with open(FIXTURE) as f:
            self.multiline = f.read()

    def test_multiline_input_i_and_input_tp(self):
        lufs, peak = vt_validate._parse_loudnorm_json(self.multiline)
        self.assertAlmostEqual(lufs, -16.23)
        self.assertAlmostEqual(peak, -1.82)

    def test_ignores_output_tp(self):
        lufs, peak = vt_validate._parse_loudnorm_json(self.multiline)
        self.assertNotAlmostEqual(peak, -1.50)

    def test_missing_input_tp(self):
        text = 'noise\n{\n  "input_i": "-14.0"\n}\n'
        lufs, peak = vt_validate._parse_loudnorm_json(text)
        self.assertAlmostEqual(lufs, -14.0)
        self.assertIsNone(peak)

    def test_malformed_json(self):
        lufs, peak = vt_validate._parse_loudnorm_json("{ broken json")
        self.assertIsNone(lufs)
        self.assertIsNone(peak)

    def test_ffmpeg_nonzero_exit(self):
        proc = mock.Mock(returncode=1, stderr="error", stdout="")
        with mock.patch("subprocess.run", return_value=proc):
            errs, lufs, peak = vt_validate.measure_loudness(
                "v.mp4", {"lufs_target": -16, "lufs_required": True}
            )
        self.assertIsNone(lufs)
        self.assertTrue(any(e["code"] == "LOUDNESS_FAILED" for e in errs))

    def test_no_subprocess_without_expectation(self):
        with mock.patch("subprocess.run") as run:
            vt_validate.measure_loudness("v.mp4", {})
            run.assert_not_called()

    def test_true_peak_exceeded(self):
        with mock.patch.object(
            vt_validate,
            "_parse_loudnorm_json",
            return_value=(-16.0, -0.5),
        ):
            with mock.patch("subprocess.run", return_value=mock.Mock(returncode=0, stderr="")):
                errs, _, peak = vt_validate.measure_loudness(
                    "v.mp4", {"true_peak_max": -1.5, "true_peak_required": True}
                )
        self.assertAlmostEqual(peak, -0.5)
        self.assertTrue(any(e["code"] == "TRUE_PEAK_EXCEEDED" for e in errs))

    def test_cli_rejects_required_without_criterion(self):
        self.assertEqual(
            vt_validate.validate_render_cli_args(
                lufs_required=True, lufs_target=None, true_peak_required=False, true_peak_max=None
            ),
            "--lufs-required requires --lufs-target",
        )


if __name__ == "__main__":
    unittest.main()