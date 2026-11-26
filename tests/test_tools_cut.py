import os
import tempfile
import unittest

from tests.tool_fixtures import py, read_json, speech_wav, write_json


class BuildEdlTest(unittest.TestCase):
    SPANS = [(0.5, 1.5), (2.5, 3.2), (5.0, 6.0)]

    def edl(self, td, check=True, **extra):
        speech_wav(os.path.join(td, "v.wav"), self.SPANS, 8.0)
        cfg = {"wav": "v.wav", "out": "edl.json", "start": 0.0, "cuts": [], "last_out": 6.6, **extra}
        write_json(os.path.join(td, "cfg.json"), cfg)
        return py("cut/build_edl.py", "cfg.json", cwd=td, check=check)

    def segments(self, td):
        return read_json(os.path.join(td, "edl.json"))["segments"]

    def test_pauses_are_compressed_and_end_is_last_out(self):
        with tempfile.TemporaryDirectory() as td:
            self.edl(td, gap=0.25)
            segs = self.segments(td)
        self.assertEqual(len(segs), 3)
        self.assertAlmostEqual(segs[-1][1], 6.6, places=2)   # `end` defaulted to last_out, not the 8 s source
        speech = sum(b - a for a, b in self.SPANS)
        self.assertLess(sum(b - a for a, b in segs), speech + 2 * 0.25 + 1.0)
        for (a, b), (s, e) in zip(self.SPANS, segs):
            self.assertLessEqual(s, a)
            self.assertGreaterEqual(e, b - 0.02)

    def test_sound_after_the_wave_is_outside_the_range(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "v.wav"), self.SPANS + [(7.4, 7.8)], 8.0)
            write_json(os.path.join(td, "cfg.json"), {"wav": "v.wav", "out": "edl.json", "start": 0.0, "cuts": [], "last_out": 6.6})
            py("cut/build_edl.py", "cfg.json", cwd=td)
            self.assertLessEqual(self.segments(td)[-1][1], 6.61)

    def test_insert_after_moves_a_range(self):
        with tempfile.TemporaryDirectory() as td:
            self.edl(td, cuts=[[0.4, 1.6]], insert_after=[[3.3, 0.4, 1.6]])
            segs = self.segments(td)
        self.assertEqual([round(v, 1) for v in segs[1]], [0.4, 1.6])

    def test_two_parts_are_two_configs_and_foreign_cuts_fail(self):
        with tempfile.TemporaryDirectory() as td:
            self.edl(td, end=4.0, last_out=None, out="edl_a.json")
            self.edl(td, start=4.0, out="edl_b.json")
            a, b = (read_json(os.path.join(td, n))["segments"] for n in ("edl_a.json", "edl_b.json"))
            self.assertLessEqual(a[-1][1], 4.0)
            self.assertGreaterEqual(b[0][0], 4.0)
            bad = self.edl(td, check=False, end=4.0, cuts=[[5.0, 5.5]])
            self.assertIn("outside this config's range", bad.stderr)

    def test_unknown_key_and_missing_end_fail(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIn("unknown keys ['gapp']", self.edl(td, check=False, gapp=1).stderr)
            self.assertIn("needs `end` or `last_out`", self.edl(td, check=False, last_out=None).stderr)


class BuildCfgTest(unittest.TestCase):
    def test_snaps_sentence_starts_and_applies_the_end_rule(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "transcript"))
            os.makedirs(os.path.join(td, "audio"))
            os.makedirs(os.path.join(td, "config"))
            speech_wav(os.path.join(td, "audio", "clean.wav"), [(1.0, 2.0), (3.0, 4.0)], 7.0)
            write_json(os.path.join(td, "transcript", "script_beats.json"), [["A1", ""], ["SKIP", ""]])
            with open(os.path.join(td, "transcript", "script_plain.md"), "w") as f:
                f.write("Hello there. Second sentence.\nignored\n")
            with open(os.path.join(td, "transcript", "ctc_src.txt"), "w") as f:
                f.write("[0-8] hello@1.05 there@1.50 second@3.10 sentence@3.50\n")
            write_json(os.path.join(td, "config", "build_cfg.json"),
                       {"first": 0.9, "bye_end": 4.0, "skip_beats": ["SKIP"]})
            py("cut/build_cfg.py", cwd=td)
            cfg = read_json(os.path.join(td, "config", "build_edl.json"))
        self.assertEqual((cfg["end"], cfg["last_out"]), (5.25, 5.2))
        self.assertEqual(len(cfg["long_before"]), 1)
        self.assertAlmostEqual(cfg["long_before"][0][0], 3.0, delta=0.05)  # energy onset, not CTC's 3.10
        self.assertEqual(cfg["long_before"][0][1], 0.25)


class RenderCutAndNudgeTest(unittest.TestCase):
    def test_filter_scripts(self):
        with tempfile.TemporaryDirectory() as td:
            write_json(os.path.join(td, "edl.json"), {"segments": [[0, 1], [2, 3]]})
            out = py("cut/render_cut.py", "1.25", cwd=td).stdout
            with open(os.path.join(td, "scripts", "voice.fg")) as f:
                voice = f.read()
            with open(os.path.join(td, "scripts", "preview.fg")) as f:
                preview = f.read()
        self.assertIn("cut_frames 60 out_frames 48", out)
        self.assertIn("atempo=1.25", voice)
        self.assertIn("setpts=PTS/1.25,fps=30", preview)

    def test_nudge_moves_a_loud_edge_to_quiet(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "a.wav"), [(1.0, 2.0)], 3.0)
            write_json(os.path.join(td, "edl.json"), {"segments": [[0.5, 1.9667]]})
            py("cut/nudge_edges.py", "--wav", "a.wav", cwd=td)
            end = read_json(os.path.join(td, "edl.json"))["segments"][0][1]
        self.assertGreater(end, 1.99)


if __name__ == "__main__":
    unittest.main()
