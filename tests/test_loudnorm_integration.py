import os
import shutil
import subprocess
import tempfile
import unittest

from tools.validate import vt_validate


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg not installed")
class LoudnormIntegrationTest(unittest.TestCase):
    def test_measure_loudness_on_synthetic_wav(self):
        with tempfile.TemporaryDirectory() as td:
            wav = os.path.join(td, "tone.wav")
            proc = subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=1",
                    "-ac",
                    "1",
                    wav,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            errs, lufs, peak = vt_validate.measure_loudness(
                wav,
                {
                    "lufs_target": -16.0,
                    "lufs_required": True,
                    "true_peak_max": 0.0,
                    "true_peak_required": True,
                },
            )
            hard = [e for e in errs if e.get("severity") == "error"]
            self.assertIsNotNone(lufs, hard)
            self.assertIsNotNone(peak, hard)


if __name__ == "__main__":
  unittest.main()