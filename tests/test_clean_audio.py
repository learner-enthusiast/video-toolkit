import tempfile
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve

from tools.clean_audio import clean, probe, wpe_dereverb


class CleanerTests(unittest.TestCase):
    def make_reverberant_voice(self, path):
        sr = 48000
        t = np.arange(sr * 4) / sr
        envelope = ((t % 0.9) < 0.55).astype(float)
        voice = envelope * (0.16 * np.sin(2 * np.pi * 170 * t) +
                            0.08 * np.sin(2 * np.pi * 340 * t) +
                            0.04 * np.sin(2 * np.pi * 680 * t))
        rir = np.zeros(int(sr * 0.65))
        rir[0] = 1
        rir[1200::2400] = np.exp(-np.arange(len(rir[1200::2400])) / 7) * 0.22
        reverberant = fftconvolve(voice, rir, mode="full")[:len(voice)]
        rng = np.random.default_rng(2026)
        reverberant += rng.normal(0, 0.001, len(reverberant))
        sf.write(path, reverberant, sr)
        return reverberant

    def test_wpe_preserves_duration_and_is_noop_at_zero_blend(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "in.wav"
            output = Path(td) / "out.wav"
            self.make_reverberant_voice(source)
            # WPE has a distinct strength control; zero blend must preserve input.
            wpe_dereverb(source, output, 0.0)
            audio, sr = sf.read(output)
            self.assertEqual(sr, 16000)
            self.assertAlmostEqual(len(audio) / sr, 4, delta=0.02)
            self.assertGreater(np.max(np.abs(audio)), 0.01)

    def test_wpe_reduces_late_tail_in_synthetic_room(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "reverb.wav"
            output = Path(td) / "dereverb.wav"
            self.make_reverberant_voice(source)
            wpe_dereverb(source, output, 0.55)
            before, _ = sf.read(source)
            after, _ = sf.read(output)
            tail = slice(int(0.60 * 16000), int(0.80 * 16000))
            rms_before = np.sqrt(np.mean(before[tail] ** 2))
            rms_after = np.sqrt(np.mean(after[tail] ** 2))
            self.assertLess(20 * np.log10(rms_after / rms_before), -3.0)

    def test_pipeline_output_and_report_keep_timeline_and_loudness(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "input.wav"
            output = Path(td) / "clean.wav"
            report = Path(td) / "report.json"
            self.make_reverberant_voice(source)
            result = clean(source, output, preset="natural", report_path=report, neural=False)
            out = probe(output)
            self.assertEqual(out["sample_rate"], 48000)
            self.assertEqual(out["channels"], 1)
            self.assertLess(abs(result["duration_delta_seconds"]), 0.03)
            self.assertTrue(report.is_file())
            self.assertIsNotNone(result["output_measurements"]["integrated_lufs"])
            self.assertLessEqual(result["output_measurements"]["true_peak_dbtp"], -1.0)


if __name__ == "__main__":
    unittest.main()
