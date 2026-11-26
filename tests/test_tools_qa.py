import os
import tempfile
import unittest

from tests.tool_fixtures import ffmpeg, py, read_json, speech_wav, write_json


def moving_video(path, seconds=3):
    """Every frame differs (testsrc2 has a running clock and moving shapes)."""
    ffmpeg("-f", "lavfi", "-i", f"testsrc2=s=128x256:r=30:d={seconds}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "1", path)


class PictureSyncTest(unittest.TestCase):
    def test_qa_sync_direct_finds_zero_offset(self):
        with tempfile.TemporaryDirectory() as td:
            moving_video(os.path.join(td, "v.mp4"))
            words = [{"raw": "start", "s": 0, "e": 5}, {"raw": "end", "s": 80, "e": 85}]
            write_json(os.path.join(td, "tl.json"),
                       {"k": 1.0, "total": 90, "words": words, "segments": [{"srcIn": 0, "from": 0, "to": 90}]})
            write_json(os.path.join(td, "cfg.json"), {"head": [[{"at": "start"}, "total"]], "rows": [0, 200]})
            out = py("qa/qa_sync_direct.py", "--video", "v.mp4", "--source", "v.mp4", "--timeline", "tl.json",
                     "--config", "cfg.json", cwd=td).stdout
        self.assertIn("median 0.0", out.strip().splitlines()[-1])

    def test_qa_sync_direct_names_a_missing_phrase(self):
        with tempfile.TemporaryDirectory() as td:
            write_json(os.path.join(td, "tl.json"), {"k": 1.0, "total": 1, "words": [], "segments": []})
            write_json(os.path.join(td, "cfg.json"), {"head": [[{"at": "old episode phrase"}, 1]]})
            r = py("qa/qa_sync_direct.py", "--video", "x", "--timeline", "tl.json", "--config", "cfg.json", cwd=td, check=False)
        self.assertIn("phrase not in timeline: 'old episode phrase'", r.stderr)

    def test_qa_sync2_best_lag_is_zero(self):
        with tempfile.TemporaryDirectory() as td:
            moving_video(os.path.join(td, "v.mp4"), 4)
            write_json(os.path.join(td, "tl.json"),
                       {"speed": 1.0, "segments": [{"outIn": 30, "outOut": 90, "srcIn": 30}]})
            out = py("qa/qa_sync2.py", "v.mp4", "v.mp4", "tl.json", "0", "0,0,128,256", cwd=td).stdout
        self.assertIn('"best_lag": 0', out)

    def test_qa_audio_lag_is_zero_for_identical_audio(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "a.wav"), [(1.0, 1.3), (1.7, 1.8), (2.4, 2.9)], 5.0, sr=48000)
            write_json(os.path.join(td, "tl.json"), {"speed": 1.0, "segments": [{"outIn": 15, "outOut": 120, "srcIn": 15}]})
            out = py("qa/qa_audio_lag.py", "a.wav", "a.wav", "tl.json", "0", cwd=td).stdout
        self.assertIn("frames 0.0", out)


class VideoInspectCpuTest(unittest.TestCase):
    def test_cpu_path_flags_a_black_flash_and_says_it_is_not_qa(self):
        with tempfile.TemporaryDirectory() as td:
            ffmpeg("-f", "lavfi", "-i", "testsrc2=s=270x480:r=30:d=4", "-f", "lavfi", "-i", "sine=f=220:d=4",
                   "-vf", "drawbox=c=black:t=fill:enable='between(t,2,2.2)'", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-shortest", os.path.join(td, "clip.mp4"))
            r = py("inspect/video_inspect.py", "clip.mp4", "--cpu-test", "--thorough", "--out-dir", "out", cwd=td)
            report = read_json(os.path.join(td, "out", "clip", "report.json"))
            self.assertTrue(os.path.getsize(os.path.join(td, "out", "clip", "contact_sheet.jpg")) > 0)
        self.assertIn("CPU TEST MODE", r.stderr)
        self.assertIn("not a QA result", report["summary"]["notes"][0])
        self.assertEqual(report["summary"]["resolution"], "270x480")
        self.assertIsNotNone(report["summary"]["lufs"])
        self.assertIn("black_flash", report["summary"]["flags"])
        self.assertEqual(report["words"], [])


if __name__ == "__main__":
    unittest.main()
