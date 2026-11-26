import json
import os
import sys
import tempfile
import unittest

from tests.tool_fixtures import py, read_json, run, speech_wav, tool, write, write_json

CAPTIONS = '### H1\nNamoshkar! Run "docker build" now.\n### B1\nThe image is one image.\n'


def heard():
    words = ["namaskar", "run", "docker", "build", "now", "the", "image", "is", "one", "image"]
    return [[0.5 + i * 0.5, 0.9 + i * 0.5, w] for i, w in enumerate(words)]


class BuildTimelineTest(unittest.TestCase):
    def build(self, config, k="1.0"):
        with tempfile.TemporaryDirectory() as td:
            write_json(os.path.join(td, "words.json"), heard())
            write(os.path.join(td, "transcript", "caption_text.md"), CAPTIONS)
            write_json(os.path.join(td, "edl.json"), {"segments": [[0, 3], [4, 6]]})
            write_json(os.path.join(td, "config", "build_timeline.json"), config)
            os.makedirs(os.path.join(td, "remotion", "public", "data"))
            out = py("captions/build_timeline.py", "words.json", k, cwd=td).stdout
            return read_json(os.path.join(td, "remotion", "public", "data", "timeline.json")), out

    def test_script_tokens_are_timed_by_the_heard_words(self):
        tl, _ = self.build({})
        self.assertEqual(tl["words"][0]["raw"], "Namoshkar!")   # built-in greeting respelling
        self.assertEqual(tl["words"][0]["s"], 15)
        self.assertEqual(tl["total"], 150 + 60)
        self.assertEqual([s["from"] for s in tl["segments"]], [0, 90])

    def test_pins_and_time_fix(self):
        tl, out = self.build({"pins": [["Namoshkar!", [[0.1, 0.8]]]], "time_fix": [["image.", 5.0, 5.2, 5.4]]})
        self.assertEqual((tl["words"][0]["s"], tl["words"][0]["e"]), (3, 24))
        self.assertEqual(tl["words"][-1]["s"], 156)      # the second "image", nearest 5.0 s
        self.assertNotEqual(tl["words"][-4]["s"], 156)
        self.assertIn("PIN 'Namoshkar!'", out)

    def test_highlight_scopes(self):
        tl, _ = self.build({"highlights": ["one [image]", "run@first"]})
        self.assertEqual([w["raw"] for w in tl["words"] if w["hl"]], ["Run", "image."])

    def test_word_fix_and_literal_marker(self):
        tl, _ = self.build({"word_fix": {"docker": "Docker", "image": "Image"},
                            "display": [["docker build", ["~docker", "~build"]]]})
        shown = [w["w"] for w in tl["words"]]
        self.assertIn("docker", shown)                  # "~docker" stays literal, tilde stripped
        self.assertNotIn("~docker", shown)
        self.assertEqual(shown.count("Image"), 2)
        tl, _ = self.build({"word_fix": {"docker": "Docker"}})
        self.assertIn("Docker", [w["w"] for w in tl["words"]])


class SrtAndPhrasesTest(unittest.TestCase):
    def timeline(self, td):
        words = [{"raw": w, "w": w.rstrip("."), "p": "." if w.endswith(".") else "", "s": i * 30, "e": i * 30 + 20}
                 for i, w in enumerate("This is the first sentence here. And this is the second one.".split())]
        write_json(os.path.join(td, "tl.json"), {"fps": 30, "total": 600, "words": words})

    def test_main_and_trailer_srt(self):
        with tempfile.TemporaryDirectory() as td:
            self.timeline(td)
            write_json(os.path.join(td, "ranges.json"), {"ranges": [[180, 360]]})
            py("captions/make_srt.py", "--timeline", "tl.json", "--out", "m.srt",
               "--trailer-ranges", "ranges.json", "--trailer-out", "t.srt", cwd=td)
            with open(os.path.join(td, "m.srt")) as f:
                main = f.read()
            with open(os.path.join(td, "t.srt")) as f:
                trailer = f.read()
        self.assertIn("first sentence here.", main)
        self.assertIn("00:00:00,000 -->", trailer)      # re-based to the trailer's own clock
        self.assertNotIn("first", trailer)

    def test_check_phrases(self):
        with tempfile.TemporaryDirectory() as td:
            self.timeline(td)
            write(os.path.join(td, "src", "plan.ts"), "at('first sentence'); at(\"not spoken\")")
            out = py("captions/check_phrases.py", "--timeline", "tl.json", "--src", "src", cwd=td).stdout
        self.assertIn("MISSING not spoken", out)
        self.assertIn("missing = 1", out)


class OnsetToolsTest(unittest.TestCase):
    def test_clamp_uses_the_energy_onset(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "v.wav"), [(1.2, 1.8)], 3.0)
            write_json(os.path.join(td, "ctc.json"), [[2.0, 2.2, "word"]])
            write_json(os.path.join(td, "wh.json"), [[1.1, 1.8, "word"]])
            py("captions/clamp_ctc.py", "--ctc", "ctc.json", "--whisper", "wh.json", "--wav", "v.wav", "--out", "o.json", cwd=td)
            self.assertAlmostEqual(read_json(os.path.join(td, "o.json"))[0][0], 1.2, delta=0.03)

    def test_retime_snaps_a_late_word_to_the_onset(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "v.wav"), [(1.0, 1.5)], 3.0)
            write_json(os.path.join(td, "tl.json"), {"fps": 30, "words": [{"w": "a", "raw": "a", "s": 33, "e": 45}]})
            py("captions/retime_onsets.py", "v.wav", "tl.json", cwd=td)
            self.assertAlmostEqual(read_json(os.path.join(td, "tl.json"))["words"][0]["s"], 0.97 * 30, delta=0.6)

    def test_fix_starts_moves_a_sentence_first_word_past_the_pause(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "v.wav"), [(0.2, 1.0), (1.6, 3.0)], 3.2)
            words = [{"w": w, "raw": r, "s": s, "e": s + 6} for w, r, s in (("end", "end.", 12), ("But", "But", 29), ("then", "then", 60))]
            write_json(os.path.join(td, "tl.json"), {"fps": 30, "words": words})
            out = py("captions/fix_starts.py", "v.wav", "tl.json", cwd=td).stdout
            self.assertIn("moved 1", out)
            self.assertAlmostEqual(read_json(os.path.join(td, "tl.json"))["words"][1]["s"], 1.57 * 30, delta=0.6)

    def test_ctc_scan_reports_a_repeated_run(self):
        with tempfile.TemporaryDirectory() as td:
            toks = "we ship it today we ship it today now".split()
            write(os.path.join(td, "ctc.txt"), "[0-8] " + " ".join(f"{w}@{i + 1}.0" for i, w in enumerate(toks)) + "\n")
            write(os.path.join(td, "s.md"), "we ship it today now\n")
            self.assertIn("INSERT", py("captions/ctc_scan.py", "ctc.txt", "s.md", cwd=td).stdout)


# Stand-ins for torch and transformers: every decode "hears" the word HI starting 0.10 s in.
FAKE_TORCH = '''
import contextlib, numpy as np
class T:
    def __init__(s, a): s.a = np.asarray(a)
    def cuda(s): return s
    def to(s, *_): return s
    def cpu(s): return s
    def numpy(s): return s.a
    def argmax(s, axis=-1): return T(s.a.argmax(axis))
    def __getitem__(s, i): return T(s.a[i])
Tensor = T
def no_grad(): return contextlib.nullcontext()
'''
FAKE_TRANSFORMERS = '''
import numpy as np, torch
VOCAB = {"<pad>": 0, "|": 1, "H": 2, "I": 3}
class _Tok:
    pad_token_id = 0
    def get_vocab(self): return VOCAB
class Wav2Vec2Processor:
    tokenizer = _Tok()
    @classmethod
    def from_pretrained(c, *_): return c()
    def __call__(s, seg, **_):
        class R: input_values = torch.T(seg)
        return R()
    def decode(s, ids): return "HI"
class Wav2Vec2ForCTC:
    @classmethod
    def from_pretrained(c, *_): return c()
    def cuda(s): return s
    def eval(s): return s
    def to(s, *_): return s
    def __call__(s, x):
        ids = [0] * 5 + [2, 3, 1] + [0] * 5
        class R: logits = torch.T(np.eye(4)[ids][None])
        return R()
'''


class CtcToolsTest(unittest.TestCase):
    """The model is stubbed; this checks the word timing and I/O around it."""

    def run_stubbed(self, td, rel, *args):
        write(os.path.join(td, "stubs", "torch.py"), FAKE_TORCH)
        write(os.path.join(td, "stubs", "transformers.py"), FAKE_TRANSFORMERS)
        return run([sys.executable, tool(rel), *args], cwd=td, env={"PYTHONPATH": os.path.join(td, "stubs")}).stdout

    def test_align_ctc(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "v.wav"), [(0.1, 0.5)], 1.0)
            write_json(os.path.join(td, "in.json"), [[0.0, 0.6, "hi"]])
            out = self.run_stubbed(td, "captions/align_ctc.py", "v.wav", "in.json", "out.json")
            start = read_json(os.path.join(td, "out.json"))[0][0]
        self.assertIn("matched 1/1", out)
        self.assertAlmostEqual(start, 0.07, places=2)

    def test_ctc_window_and_windows(self):
        with tempfile.TemporaryDirectory() as td:
            speech_wav(os.path.join(td, "v.wav"), [(0.1, 0.5)], 2.0, sr=48000)
            self.assertIn("0.0-1.0: HI", self.run_stubbed(td, "captions/ctc_window.py", "v.wav", "0", "1"))
            self.run_stubbed(td, "captions/ctc_windows.py", "v.wav", "o.txt", "env.npy", "1:2")
            with open(os.path.join(td, "o.txt")) as f:
                self.assertEqual(f.read(), "[1.0-2.0] hi@1.10\n")


if __name__ == "__main__":
    unittest.main()
