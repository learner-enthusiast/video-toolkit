import contextlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    import numpy as np
    import soundfile as sf
    from scipy.signal import fftconvolve
except ImportError:
    raise unittest.SkipTest("numpy/scipy/soundfile required (use vt-python venv for full suite)")

from tools import clean_audio
from tools.clean_audio import clean, main, probe, wpe_dereverb

# Stand-in for ~/bin/deep-filter: same flags and log lines as DeepFilterNet 0.5.6's CLI.
STUB = """#!/bin/sh
while [ $# -gt 1 ]; do case "$1" in --output-dir) OUT="$2"; shift 2;; *) shift;; esac; done
IN="$1"; NAME=$(basename "$IN")
echo "Running on device cuda:0" >&2
case "{mode}" in
  fail) echo "RuntimeError: CUDA error: out of memory" >&2; exit 3;;
  noout) ;;
  copy) cp "$IN" "$OUT/$NAME";;
  wrap) "{py}" -c "import sys, numpy as np, soundfile as sf; x, sr = sf.read(sys.argv[1]); sf.write(sys.argv[2], (x * 32768).astype(np.int64).astype(np.int16), sr, subtype='PCM_16')" "$IN" "$OUT/$NAME" || exit 4;;
  *) ffmpeg -hide_banner -loglevel error -y -i "$IN" -af volume=0.7 -c:a pcm_f32le "$OUT/$NAME" || exit 4;;
esac
[ "{mode}" = nolog ] || echo "Enhanced noisy audio file '$NAME' in 0.10s (RT factor: 0.030)" >&2
"""


def hf_share_db(path, lo=9000, hi=20000):
    a, sr = sf.read(path)
    spec = np.abs(np.fft.rfft(a)) ** 2
    f = np.fft.rfftfreq(len(a), 1 / sr)
    return 10 * np.log10(spec[(f > lo) & (f < hi)].sum() / spec.sum())


class CleanerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._td.name)
        cls.stubs = {}
        for mode in ("ok", "fail", "noout", "copy", "nolog", "wrap"):
            p = cls.dir / f"deep-filter-{mode}"
            p.write_text(STUB.replace("{mode}", mode).replace("{py}", sys.executable))
            p.chmod(p.stat().st_mode | stat.S_IXUSR)
            cls.stubs[mode] = str(p)
        cls.voice = cls.dir / "voice.wav"
        cls.make_reverberant_voice(cls.voice)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    @staticmethod
    def make_reverberant_voice(path, seconds=4, hiss=0.001):
        sr = 48000
        t = np.arange(int(sr * seconds)) / sr
        envelope = ((t % 0.9) < 0.55).astype(float)
        voice = envelope * (0.16 * np.sin(2 * np.pi * 170 * t) +
                            0.08 * np.sin(2 * np.pi * 340 * t) +
                            0.04 * np.sin(2 * np.pi * 680 * t))
        rir = np.zeros(int(sr * 0.65))
        rir[0] = 1
        rir[1200::2400] = np.exp(-np.arange(len(rir[1200::2400])) / 7) * 0.22
        reverberant = fftconvolve(voice, rir, mode="full")[:len(voice)]
        rng = np.random.default_rng(2026)
        reverberant += rng.normal(0, hiss, len(reverberant))
        sf.write(path, reverberant, sr)
        return reverberant

    def setUp(self):
        self._case = tempfile.TemporaryDirectory()
        self.work = Path(self._case.name)

    def tearDown(self):
        self._case.cleanup()

    def paths(self, rid="recording-01"):
        return self.work / "cleaned" / f"{rid}.wav", self.work / "reports" / f"{rid}-clean-report.json"

    def run_cli(self, *args):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = main([str(a) for a in args])
        return code, err.getvalue()

    def assert_failed_closed(self, out, report, stage, code, err):
        self.assertEqual(code, 1, err)
        self.assertIn("FAILED", err)
        self.assertFalse(out.exists(), "no output may be published by a failed run")
        self.assertFalse(report.exists(), "no success report may be published by a failed run")
        status = json.loads(out.with_name(out.name + ".run-status.json").read_text())
        self.assertEqual(status["status"], "failed")
        self.assertEqual(status["failed_stage"], stage)
        self.assertEqual(status["stages"][stage], "failed")
        failed = list(report.parent.glob(report.name + ".run-*.failed.json"))
        self.assertEqual(len(failed), 1)
        self.assertEqual(json.loads(failed[0].read_text())["stages"][stage], "failed")
        self.assertEqual([p for p in out.parent.iterdir() if p.suffix == ".wav" or p.name.endswith(".tmp.wav")], [])
        return status

    # --- WPE algorithm (unchanged behaviour) -------------------------------------------
    def test_wpe_preserves_duration_and_is_noop_at_zero_blend(self):
        output = self.work / "out.wav"
        wpe_dereverb(self.voice, output, 0.0)
        audio, sr = sf.read(output)
        self.assertEqual(sr, 16000)
        self.assertAlmostEqual(len(audio) / sr, 4, delta=0.02)
        self.assertGreater(np.max(np.abs(audio)), 0.01)

    def test_wpe_reduces_late_tail_in_synthetic_room(self):
        output = self.work / "dereverb.wav"
        wpe_dereverb(self.voice, output, 0.55)
        before, _ = sf.read(self.voice)
        after, _ = sf.read(output)
        tail = slice(int(0.60 * 16000), int(0.80 * 16000))
        rms_before = np.sqrt(np.mean(before[::3][tail] ** 2))
        rms_after = np.sqrt(np.mean(after[tail] ** 2))
        self.assertLess(20 * np.log10(rms_after / rms_before), -3.0)

    # --- success path --------------------------------------------------------------------
    def test_quality_pipeline_report_timeline_loudness_and_fullband(self):
        source = self.work / "hiss.wav"
        self.make_reverberant_voice(source, hiss=0.01)
        out, report = self.paths()
        code, err = self.run_cli(source, out, "--report", report, "--deepfilter-executable", self.stubs["ok"])
        self.assertEqual(code, 0, err)
        self.assertIn("automated gate: PASSED", err)
        r = json.loads(report.read_text())
        self.assertEqual(r["status"], "succeeded")
        self.assertEqual(r["stages"], {"wpe": "processed", "deepfilternet3": "processed", "mastering": "processed"})
        self.assertTrue(r["dereverberation"]["applied"])
        self.assertEqual(r["speech_enhancement"]["model"], "DeepFilterNet3")
        self.assertEqual(r["speech_enhancement"]["device"], "cuda:0")
        self.assertEqual(len(r["tone_change_db"]), 6)
        self.assertTrue(r["production_gate"]["automated_checks_passed"])
        self.assertEqual(r["input"], str(source.resolve()))
        info = probe(out)
        self.assertEqual((info["sample_rate"], info["channels"]), (48000, 1))
        self.assertLess(abs(r["duration_delta_seconds"]), 0.03)
        self.assertLessEqual(r["output_measurements"]["true_peak_dbtp"], -1.0)
        self.assertLess(abs(r["output_measurements"]["integrated_lufs"] + 16), 1.0)
        status = json.loads(out.with_name(out.name + ".run-status.json").read_text())
        self.assertEqual((status["status"], status["run_id"]), ("succeeded", r["run_id"]))
        # Content above 8 kHz must survive (the old 16 kHz WPE merge removed ~43 dB of it).
        self.assertGreater(hf_share_db(out), hf_share_db(source) - 12)
        self.assertEqual(sf.info(source).samplerate, 48000)  # source untouched

    def test_balanced_mode_runs_but_never_passes_the_gate(self):
        out, report = self.paths()
        code, err = self.run_cli(self.voice, out, "--report", report, "--mode", "balanced")
        self.assertEqual(code, 0, err)
        r = json.loads(report.read_text())
        self.assertEqual(r["stages"]["deepfilternet3"], "disabled")
        self.assertFalse(r["production_gate"]["automated_checks_passed"])
        self.assertIn("NOT PASSED", err)

    # --- configuration rejected in quality mode ------------------------------------------
    def test_quality_mode_rejects_disabled_or_zeroed_stages(self):
        out, report = self.paths()
        with self.assertRaisesRegex(ValueError, "DeepFilterNet3"):
            clean(self.voice, out, report_path=report, neural=False)
        for cfg in ({"dereverb_enabled": False}, {"speech_enhancement_enabled": False},
                    {"dereverb_strength": 0}, {"enhancement_strength": 0}, {"dereverb_enable": True}):
            path = self.work / "cfg.json"
            path.write_text(json.dumps(cfg))
            code, err = self.run_cli(self.voice, out, "--report", report, "--config", path,
                                     "--deepfilter-executable", self.stubs["ok"])
            self.assertEqual(code, 1, cfg)
            self.assertFalse(out.exists(), cfg)

    def test_cli_help_has_no_neural_switch(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            main(["--help"])
        self.assertNotIn("--no-neural", buf.getvalue())
        self.assertIn("quality", buf.getvalue())

    # --- WPE failures --------------------------------------------------------------------
    def test_wpe_missing_dependency_fails(self):
        out, report = self.paths()
        with mock.patch.object(clean_audio, "wpe_fullband", side_effect=ImportError("No module named 'scipy'")):
            code, err = self.run_cli(self.voice, out, "--report", report, "--deepfilter-executable", self.stubs["ok"])
        status = self.assert_failed_closed(out, report, "wpe", code, err)
        self.assertEqual(status["stages"]["deepfilternet3"], "not_attempted")

    def test_wpe_linalg_error_fails(self):
        out, report = self.paths()
        with mock.patch("numpy.linalg.solve", side_effect=np.linalg.LinAlgError("singular")):
            code, err = self.run_cli(self.voice, out, "--report", report, "--deepfilter-executable", self.stubs["ok"])
        self.assert_failed_closed(out, report, "wpe", code, err)
        self.assertIn("numerical failure", err)

    def test_wpe_short_recording_fails(self):
        source = self.work / "short.wav"
        sf.write(source, 0.1 * np.sin(np.arange(2400) / 5), 48000)  # 50 ms
        out, report = self.paths()
        code, err = self.run_cli(source, out, "--report", report, "--deepfilter-executable", self.stubs["ok"])
        self.assert_failed_closed(out, report, "wpe", code, err)
        self.assertIn("too short", err)

    # --- DeepFilterNet failures ----------------------------------------------------------
    def test_deepfilternet_failures_fail_closed(self):
        cases = {"missing": str(self.work / "nope" / "deep-filter"), "fail": self.stubs["fail"],
                 "noout": self.stubs["noout"], "copy": self.stubs["copy"], "nolog": self.stubs["nolog"]}
        for name, exe in cases.items():
            with self.subTest(name):
                out, report = self.paths(f"rec-{name}")
                code, err = self.run_cli(self.voice, out, "--report", report, "--deepfilter-executable", exe)
                status = self.assert_failed_closed(out, report, "deepfilternet3", code, err)
                self.assertEqual(status["stages"]["wpe"], "processed")
                self.assertEqual(status["stages"]["mastering"], "not_attempted")

    def test_failure_keeps_previous_verified_output_and_marks_run_failed(self):
        out, report = self.paths()
        self.assertEqual(self.run_cli(self.voice, out, "--report", report, "--deepfilter-executable", self.stubs["ok"])[0], 0)
        first = json.loads(report.read_text())["run_id"]
        code, _ = self.run_cli(self.voice, out, "--report", report, "--deepfilter-executable", self.stubs["fail"])
        self.assertEqual(code, 1)
        status = json.loads(out.with_name(out.name + ".run-status.json").read_text())
        self.assertEqual(status["status"], "failed")
        self.assertTrue(status["previous_output_preserved"])
        self.assertNotEqual(status["run_id"], first)  # report's run_id no longer matches: not a verified current run

    # --- hot input: DeepFilterNet's unclamped int16 save must never see overs -------------
    def make_hot_stereo(self, path):
        voice = self.make_reverberant_voice(self.work / "mono.wav")
        # Dual-mono phone audio: identical channels. FFmpeg's -ac 1 adds them at 1/sqrt(2) each (+3 dB),
        # so 0.802 per channel became 1.134 on 07-provider-failover. 1.1 per channel -> ~1.56 mono, which
        # stays over full scale even after WPE trims this fixture's synthetic reverb.
        x = voice / np.max(np.abs(voice)) * 1.1
        sf.write(path, np.stack([x, x], axis=1), 48000, subtype="FLOAT")

    def test_hot_stereo_gets_headroom_and_no_wrapped_clicks(self):
        source = self.work / "hot.wav"
        self.make_hot_stereo(source)
        out, report = self.paths()
        code, err = self.run_cli(source, out, "--report", report, "--deepfilter-executable", self.stubs["wrap"])
        self.assertEqual(code, 0, err)
        r = json.loads(report.read_text())
        self.assertLess(r["processing_headroom_gain_db"], -2.0)
        self.assertEqual(r["stages"]["deepfilternet3"], "processed")
        y, _ = sf.read(out)
        self.assertLess(np.max(np.abs(np.diff(y))), 0.5)   # no wrap-around discontinuities
        self.assertLessEqual(max(abs(v) for v in r["tone_change_db"].values()), 6.0)

    def test_wrapped_deepfilternet_output_fails_closed(self):
        source = self.work / "hot.wav"
        self.make_hot_stereo(source)
        out, report = self.paths()
        with mock.patch.object(clean_audio, "_headroom", return_value=(0.0, 1.2)):
            code, err = self.run_cli(source, out, "--report", report, "--deepfilter-executable", self.stubs["wrap"])
        self.assert_failed_closed(out, report, "deepfilternet3", code, err)
        self.assertIn("wrapped", err)

    # --- path safety ---------------------------------------------------------------------
    def test_raw_protected_and_reports_distinct_per_recording(self):
        raw = self.work / "raw"
        raw.mkdir()
        with self.assertRaisesRegex(ValueError, "protected"):
            clean(self.voice, raw / "clean.wav")
        other = self.work / "other.wav"
        self.make_reverberant_voice(other, seconds=2)
        out1, report = self.paths("recording-01")
        self.assertEqual(self.run_cli(self.voice, out1, "--report", report, "--deepfilter-executable", self.stubs["ok"])[0], 0)
        out2, _ = self.paths("recording-02")
        with self.assertRaisesRegex(ValueError, "belongs to another recording"):
            clean(other, out2, report_path=report, deepfilter_executable=self.stubs["ok"])
        self.assertEqual(json.loads(report.read_text())["input"], str(self.voice.resolve()))


class PreflightTests(unittest.TestCase):
    def test_preflight_fails_with_fix_when_deepfilternet_is_missing(self):
        from tools import voice_preflight
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = voice_preflight.main(["--deepfilter-executable", "/nonexistent/deep-filter"])
        self.assertEqual(code, 1)
        self.assertIn("FAIL DeepFilterNet launcher", out.getvalue())
        self.assertIn("fix:", out.getvalue())
        self.assertIn("NOT READY", out.getvalue())

    def test_lock_pins_the_known_good_pair(self):
        from tools.voice_preflight import pinned_versions
        pins = pinned_versions()
        self.assertEqual((pins["torch"], pins["torchaudio"], pins["deepfilternet"]), ("2.6.0+cu126", "2.6.0+cu126", "0.5.6"))


if __name__ == "__main__":
    unittest.main()
