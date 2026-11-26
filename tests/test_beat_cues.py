"""Beat IDs and named cues: the script parser, the timeline, resolve_cues.py and cues.ts."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.tool_fixtures import REPO, py, read_json, write, write_json
from tools.captions import resolve_cues as rc
from tools.scaffold_remotion import scaffold
from tools.script_beats import id_problems, parse_beats


class ScriptBeatsTest(unittest.TestCase):
    def test_tags_with_and_without_times_and_ids(self):
        text = ('`[B01 | 00:00–00:03 | HEAD]` · "hook"\n[B02 | HEAD] Namoshkar!\n'
                '[B07 | SPLIT | tableScan="poori table"] line\nold `[00:02-00:08 | FULL]`\n'
                'format: `[Bnn | mm:ss–mm:ss | HEAD, FULL or SPLIT]` and `[mm:ss–mm:ss | STATE]`\n')
        beats = parse_beats(text)
        self.assertEqual([(b["id"], b["state"]) for b in beats],
                         [("B01", "HEAD"), ("B02", "HEAD"), ("B07", "SPLIT"), (None, "FULL")])
        self.assertEqual(beats[0]["start"], "00:00")
        self.assertIn('tableScan="poori table"', beats[2]["rest"])

    def test_id_rules(self):
        self.assertEqual(id_problems([None, None]), [])           # a script from before beat IDs
        self.assertEqual(id_problems(["B01", "B02", "B05"]), [])
        self.assertIn("no ID", id_problems(["B01", None])[0])
        self.assertIn("repeated", id_problems(["B01", "B01"])[0])
        self.assertIn("out of order", id_problems(["B02", "B01"])[0])

    def test_cli_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            write(os.path.join(td, "s.md"), "[B02 | HEAD] a\n[B01 | HEAD] b\n")
            self.assertEqual(py("script_beats.py", "s.md", cwd=td, check=False).returncode, 1)


def timeline(*rows):
    """rows: (beat, 'raw words'); word i lasts 8 frames and starts at 10*i + 0.5."""
    words, i = [], 0
    for beat, text in rows:
        for raw in text.split():
            words.append({"raw": raw, "w": raw, "s": 10 * i + 0.5, "e": 10 * i + 8.5, "b": beat})
            i += 1
    return words


WORDS = timeline(("B01", "Your bill is high."), ("B02", "Namoshkar!"),
                 ("B07", "A one-time full table scan, 5 times. The table's full table."),
                 ("B08", "full table again"))


def resolve(**cues):
    return rc.resolve({name.replace("__", "."): spec for name, spec in cues.items()}, WORDS)


def spec(beat, phrase, **extra):
    return {"beat": beat, "phrase": phrase, **extra}


class ResolveTest(unittest.TestCase):
    def test_same_matching_rules_as_at(self):
        frames, errors = resolve(
            B07__oneTime=spec("B07", "a one-time"),       # hyphenated word is one token
            B07__five=spec("B07", "five times"),          # number word equals the digit
            B07__owner=spec("B07", "THE table's"),        # case and apostrophe ignored
            B01__billEnd=spec("B01", "bill is high", edge="end"))
        self.assertEqual(errors, [])
        self.assertEqual(frames["B07.oneTime"], 51)       # JavaScript rounding: 50.5 -> 51 (round() gives 50)
        self.assertEqual(frames["B07.five"], 10 * 10 + 1)
        self.assertEqual(frames["B01.billEnd"], 39)       # end of "high." = 38.5 -> 39

    def test_matches_are_scoped_to_the_beat(self):
        frames, errors = resolve(B08__again=spec("B08", "full table"), B01__scan=spec("B01", "full table"))
        self.assertIn("B08.again", frames)
        self.assertIn("is not in B01 (it is in B07, B08)", errors[0])

    def test_a_phrase_may_run_into_the_next_beat(self):
        frames, errors = resolve(B01__cross=spec("B01", "high Namoshkar"))
        self.assertEqual((frames["B01.cross"], errors), (31, []))

    def test_ambiguity_needs_from(self):
        _, errors = resolve(B07__table=spec("B07", "full table"))
        self.assertIn("ambiguous in B07", errors[0])
        frames, errors = resolve(
            B07__first=spec("B07", "full table", **{"from": 0}),
            B07__second=spec("B07", "full table", **{"from": "B07.first+5"}),
            B07__before=spec("B07", "table", **{"from": "B07.second - 5"}))
        self.assertEqual(errors, [])
        self.assertLess(frames["B07.first"], frames["B07.second"])
        self.assertGreater(frames["B07.before"], frames["B07.second"])

    def test_forward_references_resolve_and_loops_fail(self):
        frames, errors = resolve(B07__b=spec("B07", "full table", **{"from": "B07.a+1"}),
                                 B07__a=spec("B07", "full table", **{"from": 0}))
        self.assertEqual(errors, [])
        _, errors = resolve(B07__a=spec("B07", "scan", **{"from": "B07.b"}), B07__b=spec("B07", "scan", **{"from": "B07.a"}))
        self.assertIn("loops", " ".join(errors))

    def test_bad_entries_are_all_reported(self):
        _, errors = resolve(
            B07__gone=spec("B07", "no such words"), B07__late=spec("B07", "scan", **{"from": 9999}),
            B08__wrongName=spec("B07", "scan"), B09__noBeat=spec("B09", "scan"),
            B07__empty=spec("B07", "..."), B07__extra=spec("B07", "scan", nth=2), B07__edge=spec("B07", "scan", edge="mid"))
        self.assertEqual(len(errors), 7, errors)

    def test_beat_spans_end_at_the_next_beat(self):
        spans = rc.beat_spans(WORDS)
        self.assertEqual(spans["B01"], (0.5, 40.5))
        self.assertEqual(spans["B08"][1], WORDS[-1]["e"])


class ResolveCliTest(unittest.TestCase):
    def run_cli(self, td, cues, code="cue('B07.scan'); beatAt('B07', 0.4)"):
        write_json(os.path.join(td, "public", "data", "timeline.json"), {"words": WORDS})
        write_json(os.path.join(td, "public", "data", "cues.json"), cues)
        write(os.path.join(td, "src", "scenes", "a.tsx"), code)
        return py("captions/resolve_cues.py", "--src", "src", cwd=td, check=False)

    def test_writes_frames_and_lists_unused(self):
        with tempfile.TemporaryDirectory() as td:
            r = self.run_cli(td, {"B07.scan": spec("B07", "scan"), "B07.spare": spec("B07", "one-time")})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(set(read_json(os.path.join(td, "public", "data", "cue_frames.json"))), {"B07.scan", "B07.spare"})
        self.assertIn("unused in src: B07.spare", r.stdout)

    def test_any_failure_writes_nothing(self):
        for cues, code, why in (
            ({"B07.scan": spec("B07", "nope")}, "cue('B07.scan')", "is not in B07"),
            ({}, "cue('B07.scan')", "not in cues.json"),
            ({}, "beatAt('B99')", "has no words"),
            ({}, "beatAt('B07', 1.5)", "must be 0..1")):
            with self.subTest(why=why), tempfile.TemporaryDirectory() as td:
                r = self.run_cli(td, cues, code)
                self.assertEqual(r.returncode, 1)
                self.assertIn(why, r.stderr)
                self.assertFalse(os.path.exists(os.path.join(td, "public", "data", "cue_frames.json")))


class TimelineBeatsTest(unittest.TestCase):
    def build(self, captions, check=True):
        with tempfile.TemporaryDirectory() as td:
            write_json(os.path.join(td, "words.json"), [[0.5, 0.9, "one"], [1.0, 1.4, "two"], [2.0, 2.4, "three"]])
            write(os.path.join(td, "transcript", "caption_text.md"), captions)
            write_json(os.path.join(td, "edl.json"), {"segments": [[0, 3]]})
            write_json(os.path.join(td, "config", "build_timeline.json"), {})
            os.makedirs(os.path.join(td, "remotion", "public", "data"))
            r = py("captions/build_timeline.py", "words.json", "1.0", cwd=td, check=check)
            path = os.path.join(td, "remotion", "public", "data", "timeline.json")
            return r, read_json(path) if os.path.exists(path) else None

    def test_timeline_beats_carry_their_ids(self):
        _, tl = self.build("### B01\none two\n### B02\nthree\n")
        self.assertEqual(tl["beats"], [{"id": "B01", "words": [0, 1]}, {"id": "B02", "words": [2, 2]}])
        self.assertEqual([w["b"] for w in tl["words"]], ["B01", "B01", "B02"])

    def test_projects_without_ids_still_build(self):
        _, tl = self.build("### H1\none two\n### C2\nthree\n")
        self.assertEqual([b["id"] for b in tl["beats"]], ["H1", "C2"])

    def test_bad_beat_headings_fail(self):
        for captions, why in (("### B01\none\n### B01\ntwo three\n", "repeated beat IDs"),
                              ("### B01\none two\n### Close\nthree\n", "mix of beat IDs")):
            r, tl = self.build(captions, check=False)
            self.assertIn(why, r.stderr)
            self.assertIsNone(tl)


class CuesTsTest(unittest.TestCase):
    def test_scaffold_ships_the_library_and_empty_data(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "p"))
            root = scaffold(os.path.join(td, "p"), "9:16")
            with open(os.path.join(root, "src", "lib", "cues.ts")) as f, \
                    open(os.path.join(REPO, "templates", "remotion", "cues.ts")) as g:
                self.assertEqual(f.read(), g.read())
            self.assertEqual(read_json(os.path.join(root, "public", "data", "cues.json")), {})
            self.assertTrue(read_json(os.path.join(root, "tsconfig.json"))["compilerOptions"]["resolveJsonModule"])

    def test_typescript_beat_spans_match_python(self):
        node = shutil.which("node")
        if not node or subprocess.run([node, "--experimental-strip-types", "-e", ""], capture_output=True).returncode:
            self.skipTest("node without TypeScript type stripping")
        with open(os.path.join(REPO, "templates", "remotion", "cues.ts")) as f:
            source = f.read()
        data = (f"const timeline = {json.dumps({'words': WORDS})};\nconst cueFrames = {{'B07.scan': 123}};\n")
        source = "\n".join(l for l in source.splitlines() if not l.startswith("import ")) + "\n"
        calls = [("B01", 0), ("B01", 0.5), ("B07", 0.4), ("B08", 1)]
        source = data + source + ("console.log(JSON.stringify([cue('B07.scan'), "
                                  + ", ".join(f"beatAt('{b}', {x})" for b, x in calls) + "]));\n")
        with tempfile.TemporaryDirectory() as td:
            write(os.path.join(td, "c.ts"), source)
            out = subprocess.run([node, "--experimental-strip-types", os.path.join(td, "c.ts")],
                                 capture_output=True, text=True, check=True).stdout
        spans = rc.beat_spans(WORDS)
        expected = [123] + [rc.frame(spans[b][0] + x * (spans[b][1] - spans[b][0])) for b, x in calls]
        self.assertEqual(json.loads(out), expected)


if __name__ == "__main__":
    unittest.main()
