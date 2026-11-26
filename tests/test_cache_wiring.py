"""The caches as the pipeline docs call them: as scripts, from any folder."""
import json
import os
import sys
import tempfile
import unittest

from tests.tool_fixtures import TOOLS, ffmpeg, read_json, run, speech_wav, tool, write, write_json
from tools import cache_events


def cli(rel, *args, cwd, **kw):
    return run([sys.executable, tool(rel), *args], cwd=cwd, check=False, **kw)


def results(project):
    return [(e["cache"], e["op"], e["result"], e["reason"]) for e in cache_events.read(project) or []]


class ProbeCacheTest(unittest.TestCase):
    def test_default_entries_probe_rotation_fps_and_audio_then_hit(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            src = os.path.join(td, "a.mp4")
            ffmpeg("-f", "lavfi", "-i", "testsrc2=s=64x128:r=30:d=1", "-f", "lavfi", "-i", "sine=d=1", "-shortest", src)
            first = cli("asset_cache.py", "ffprobe", proj, src, cwd=td)
            second = cli("asset_cache.py", "ffprobe", proj, src, cwd=td)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            data = read_json(first.stdout.strip())
            self.assertEqual([r[2] for r in results(proj)], ["miss", "hit"])
        video = next(s for s in data["streams"] if s["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"], video["r_frame_rate"]), (64, 128, "30/1"))
        self.assertIn("sample_rate", next(s for s in data["streams"] if s["codec_type"] == "audio"))
        self.assertIn("duration", data["format"])


class VoiceCacheTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.proj = os.path.join(self.td.name, "p")
        os.makedirs(self.proj)
        self.src = os.path.join(self.td.name, "take.wav")
        self.wav = os.path.join(self.proj, "clean.wav")
        self.report = os.path.join(self.proj, "report.json")
        speech_wav(self.src, [(0.1, 0.4)], 1.0)
        speech_wav(self.wav, [(0.1, 0.4)], 1.0, sr=48000)
        self.write_report()

    def tearDown(self):
        self.td.cleanup()

    def write_report(self, **over):
        report = {"status": "succeeded", "run_id": "r1", "preset": "studio", "mode": "quality",
                  "input": self.src, "output": self.wav, "production_gate": {"automated_checks_passed": True}}
        write_json(self.report, {**report, **over})

    def voice(self, cmd, *extra):
        return cli("asset_cache.py", cmd, self.proj, self.src, self.wav, "--report", self.report, *extra, cwd=self.td.name)

    def reason(self, *extra):
        return json.loads(self.voice("voice-lookup", *extra).stdout)["reason"]

    def test_reuse_needs_same_source_preset_mode_wav_and_report(self):
        self.assertEqual(self.reason(), "miss")
        self.assertEqual(self.voice("voice-store").returncode, 0)
        self.assertEqual(self.reason(), "hit")
        self.assertEqual(self.reason("--mode", "balanced"), "miss")
        self.assertEqual(self.reason("--preset", "light"), "miss")
        self.write_report(run_id="r2")
        self.assertEqual(self.reason(), "report_differs")
        self.write_report()
        speech_wav(self.wav, [(0.2, 0.6)], 1.0, sr=48000)
        self.assertEqual(self.reason(), "wav_differs")
        speech_wav(self.src, [(0.5, 0.9)], 1.0)
        self.assertEqual(self.reason(), "miss")

    def test_a_changed_cleaner_misses(self):
        from tools import asset_cache as ac
        self.assertEqual(self.voice("voice-store").returncode, 0)
        entry = next(iter(ac.load_manifest(self.proj)["entries"].values()))
        self.assertEqual(entry["script_hash"], ac.sha256_file(os.path.join(TOOLS, "clean_audio.py"))[:16])
        other = os.path.join(self.td.name, "clean_audio_changed.py")
        write(other, "# a different implementation\n")
        found = ac.lookup(self.proj, self.src, "voice_clean",
                          {"preset": "studio", "mode": "quality", "config_sha256": None}, script=other)
        self.assertFalse(found["hit"])

    def test_a_report_that_failed_the_gate_is_never_cached(self):
        for over, why in (({"production_gate": {"automated_checks_passed": False}}, "report_gate_not_passed"),
                          ({"status": "failed"}, "report_not_succeeded"),
                          ({"input": "/elsewhere.wav"}, "report_is_for_another_source"),
                          ({"mode": "balanced"}, "report_preset_or_mode_differs")):
            with self.subTest(why=why):
                self.write_report(**over)
                r = self.voice("voice-store")
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(why, r.stderr)
        self.assertEqual(self.reason(), "miss")


class WhisperCacheTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.work = os.path.join(self.td.name, "work")
        os.makedirs(self.work)
        speech_wav(os.path.join(self.work, "voice.wav"), [(0.1, 0.4)], 1.0)
        bin_ = os.path.join(self.td.name, "bin")
        # Writes a JSON into --output_dir unless FAKE_OOM is set (the real tool exits 0 on OOM).
        write(os.path.join(bin_, "gpu-run"), f'''#!/bin/bash
echo "$*" >> "{self.td.name}/calls"
[ -n "$FAKE_OOM" ] && exit 0
while [ $# -gt 0 ]; do [ "$1" = --output_dir ] && out=$2; shift; done
echo '{{"segments": []}}' > "$out/voice.json"
''', executable=True)
        write(os.path.join(bin_, "whisper-ctranslate2"), "#!/bin/bash\necho whisper 1.0\n", executable=True)
        self.env = {"PATH": bin_ + os.pathsep + os.environ["PATH"]}

    def tearDown(self):
        self.td.cleanup()

    def pass_(self, *args, env=None):
        return cli("captions/transcribe.py", self.td.name, "voice.wav", "--out-dir", "transcript/A", *args,
                   cwd=self.work, env={**self.env, **(env or {})})

    def calls(self):
        path = os.path.join(self.td.name, "calls")
        if not os.path.isfile(path):
            return []
        with open(path) as f:
            return f.read().splitlines()

    def test_same_wav_and_flags_reuse_changed_flags_or_audio_rerun(self):
        flags = ("--", "--compute_type", "int8", "--best_of", "1")
        self.assertIn("CACHE STORE", self.pass_(*flags).stdout)
        self.assertIn("CACHE HIT", self.pass_(*flags).stdout)
        self.assertEqual(len(self.calls()), 1)
        self.assertIn("--device cuda", self.calls()[0])
        self.assertIn("--compute_type int8 --best_of 1", self.calls()[0])
        self.assertIn("CACHE STORE", self.pass_("--", "--compute_type", "int8_float16").stdout)
        speech_wav(os.path.join(self.work, "voice.wav"), [(0.5, 0.9)], 1.0)
        self.assertIn("CACHE STORE", self.pass_(*flags).stdout)
        self.assertEqual(len(self.calls()), 3)

    def test_exit_zero_without_json_fails_and_caches_nothing(self):
        r = self.pass_(env={"FAKE_OOM": "1"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no readable JSON", r.stderr)
        self.assertIn("CACHE STORE", self.pass_().stdout)

    def test_device_cannot_be_overridden(self):
        r = self.pass_("--", "--device", "cpu")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.calls(), [])


class InspectCacheCliTest(unittest.TestCase):
    def test_runs_as_a_script_and_final_qa_is_a_bypass_not_a_miss(self):
        with tempfile.TemporaryDirectory() as td:
            video = os.path.join(td, "v.mp4")
            ffmpeg("-f", "lavfi", "-i", "color=s=64x64:d=1", video)
            miss = cli("inspect_cache.py", "lookup", td, video, "--mode", "default", cwd=td)
            final = cli("inspect_cache.py", "lookup", td, video, "--mode", "thorough", "--for-final", cwd=td)
            self.assertEqual(json.loads(final.stdout)["reason"], "final_qa_requires_fresh_run", final.stderr)
            self.assertEqual(json.loads(miss.stdout)["hit"], False)
            self.assertEqual([r[2] for r in results(td)], ["miss", "bypass"])


if __name__ == "__main__":
    unittest.main()
