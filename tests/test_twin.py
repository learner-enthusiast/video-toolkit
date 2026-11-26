"""Hindi twin tools: project setup, gate, cue mapping, trailer ranges, Remotion links, QA and metrics."""
import json
import os
import tempfile
import unittest

from tests.tool_fixtures import REPO, ffmpeg, py, read_json, write, write_json
from tools import project_state as pst, stage_record, vt_log
from tools.inspect import caption_reference
from tools.twin import common, gate, map_cues as mc, new_twin, save_hindi_script, setup_remotion, trailer_ranges as tr
from tools.validate import vt_validate


def words(*rows, step=15, length=10, start=0):
    """rows: (beat, 'raw words'); word i starts at start + step*i."""
    out, i = [], 0
    for beat, text in rows:
        for raw in text.split():
            out.append({"raw": raw, "w": raw, "s": start + step * i, "e": start + step * i + length, "b": beat})
            i += 1
    return out


HINDI_SCRIPT = '''# Script (Hindi, romanized)
[B01 | HEAD] aapka bill zyada hai
[B02 | HEAD] Namoshkar!
[B03 | SPLIT | scan="poori table"] har request poori table padhta hai

## 60-second cut
B01, B02–B03
'''


class World:
    """A delivered English project and its twin, in a temp projects/ folder."""

    def __init__(self, td, delivered=True, named_cues=True, trailer_data=True):
        self.english = os.path.join(td, "projects", "demo")
        r = os.path.join(self.english, "work", "remotion")
        for d in ("raw", "out", "work"):
            os.makedirs(os.path.join(self.english, d), exist_ok=True)
        log = "# demo log\n"
        if delivered:
            log += "\n**Final QA:** pass\n**Approval:** final=approved\n"
            write(os.path.join(self.english, "out", "demo-video_9x16.mp4"), "x")
        write(os.path.join(self.english, "log.md"), log)
        code = "import {cue} from './lib/cues';\nexport const T = {scan: cue('B03.scan')};\n"
        if not named_cues:
            code = "export const T = {scan: at('full table')};\n"
        if trailer_data:
            code += "import {trailerRanges} from './lib/cues';\nexport const TRAILER = trailerRanges;\n"
        write(os.path.join(r, "src", "plan.ts"), code)
        write(os.path.join(r, "src", "lib", "cues.ts"), "export const trailerRanges = [];\n")
        write(os.path.join(r, "scripts", "export_cues.ts"), "// exporter\n")
        for name in ("package.json", "tsconfig.json", "remotion.config.ts"):
            write(os.path.join(r, name), "{}")
        os.makedirs(os.path.join(r, "node_modules"))
        for name in ("main.mp4", "voice.wav", "backdrop.jpg", "cutout.png"):
            write(os.path.join(r, "public", name), "english " + name)
        write(os.path.join(r, "public", "sfx", "pop.wav"), "pop")
        os.symlink(os.path.join(REPO, "icons"), os.path.join(r, "public", "icons"))
        data = os.path.join(r, "public", "data")
        self.en_words = words(("B01", "your bill is high"), ("B02", "Namoshkar!"), ("B03", "every request reads the full table now"))
        write_json(os.path.join(data, "timeline.json"), {"fps": 30, "total": 300, "words": self.en_words})
        cues = {"B03.scan": {"beat": "B03", "phrase": "full table"}} if named_cues else {}
        write_json(os.path.join(data, "cues.json"), cues)
        write_json(os.path.join(data, "cue_frames.json"), {"B03.scan": 150} if cues else {})
        write_json(os.path.join(data, "trailer_ranges.json"), {"ranges": [[0, 55], [72, 190]]})
        write_json(os.path.join(data, "face.json"), {"english": True})
        write_json(os.path.join(data, "slides.json"), {"s": 1})
        self.data = data
        self.twin = new_twin.create(self.english)
        write(os.path.join(self.twin, "script.md"), HINDI_SCRIPT)


class NewTwinAndScriptTest(unittest.TestCase):
    def test_twin_state_and_folders(self):
        with tempfile.TemporaryDirectory() as td:
            w = World(td)
            self.assertTrue(w.twin.endswith("demo-hi"))
            state = common.read_state(w.twin)
            self.assertEqual((state["twin_of"], state["language"]), ("demo", "hi"))
            self.assertIsNone(vt_validate.check_state_schema(w.twin) or None)
            pst.sync_handoff(w.twin)                                    # a rebuild keeps the twin fields
            self.assertEqual(common.read_state(w.twin)["twin_of"], "demo")
            new_twin.create(w.english)                                  # again: nothing is overwritten
            with open(os.path.join(w.twin, "script.md")) as f:
                self.assertEqual(f.read(), HINDI_SCRIPT)
            with self.assertRaises(SystemExit):
                new_twin.create(w.twin)

    def test_english_prompt_section_is_saved_and_nothing_else(self):
        prompt = ('# Build: x\n\n# Script\nEnglish\n\n## 60-second cut\nenglish cut\n\n# Hindi script\n'
                  '[B01 | HEAD] pehli line\n[B02 | HEAD] Namoshkar!\n\n## Hindi 60-second cut\nB01, B02\n\n# Notes\nno\n')
        with tempfile.TemporaryDirectory() as td:
            english = os.path.join(td, "projects", "demo")
            write(os.path.join(td, "prompt.md"), prompt)
            os.makedirs(english)
            py("twin/save_hindi_script.py", english, "prompt.md", cwd=td)
            self.assertEqual(os.listdir(english + "-hi"), ["script.md"])
            with open(os.path.join(english + "-hi", "script.md")) as f:
                saved = f.read()
            self.assertIn("pehli line", saved)
            self.assertIn("## Hindi 60-second cut", saved)
            for other in ("english cut", "# Notes", "English\n"):
                self.assertNotIn(other, saved)
            write(os.path.join(td, "none.md"), "# Script\nonly english\n")
            self.assertEqual(py("twin/save_hindi_script.py", english, "none.md", cwd=td, check=False).returncode, 3)

    def test_the_hindi_prompt_template_keeps_its_short_cut(self):
        with open(os.path.join(REPO, "templates", "editing-prompt-hindi.md")) as f:
            saved = save_hindi_script.extract(f.read())
        self.assertIn("## 60-second cut", saved)
        self.assertIn('tableScan="poori table"', saved)


class GateTest(unittest.TestCase):
    def reasons(self, **kw):
        with tempfile.TemporaryDirectory() as td:
            return " | ".join(gate.problems(World(td, **kw).twin))

    def test_a_delivered_approved_project_with_named_cues_passes(self):
        self.assertEqual(self.reasons(), "")

    def test_refusals(self):
        undelivered = self.reasons(delivered=False)
        for why in ("final approval", "passed final QA", "no single delivered main video"):
            self.assertIn(why, undelivered)
        old_style = self.reasons(named_cues=False)
        self.assertIn("no named cues", old_style)
        self.assertIn("still call at()", old_style)
        self.assertIn("trailerRanges", self.reasons(trailer_data=False))

    def test_latest_final_qa_line_wins_and_missing_beats_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            w = World(td)
            py("project_state.py", "record-final-qa", w.english, "fail", cwd=td)
            self.assertIn("passed final QA", " ".join(gate.problems(w.twin)))
            py("project_state.py", "record-final-qa", w.english, "pass", cwd=td)
            write(os.path.join(w.twin, "script.md"), "[B01 | HEAD] sirf ek\n")
            self.assertIn("lacks beats the English cues use: B03", " ".join(gate.problems(w.twin)))
            r = py("twin/gate.py", w.twin, cwd=td, check=False)
            self.assertEqual(r.returncode, 1)
            self.assertIn("REFUSED", r.stdout)


class MapCuesTest(unittest.TestCase):
    # words fill their slots (28 of 30 frames), so there are no pauses unless a test makes one
    EN = {"fps": 30, "words": words(("B01", "a b c d"), ("B02", "e f g h i j"), step=30, length=28)}

    def hindi(self, step=30, gap_after=None):
        w = words(("B01", "ek do teen chaar"), ("B02", "har request poori table padhta hai"), step=step, length=step - 2)
        if gap_after is not None:
            w[gap_after]["e"] = w[gap_after]["s"] + 4
        return {"fps": 30, "words": w}

    def run_map(self, cues, frames, hindi, anchors=None):
        cues = {name: {"beat": name.split(".")[0], "phrase": "x", **extra} for name, extra in cues.items()}
        return mc.map_cues(cues, frames, self.EN, hindi, anchors or {})

    def test_anchor_beats_relative(self):
        frames, report = self.run_map({"B02.scan": {}}, {"B02.scan": 180}, self.hindi(),
                                      {"B02.scan": "poori table"})
        self.assertEqual(frames["B02.scan"], 180)      # "poori" is Hindi word 6
        self.assertEqual(report["cues"]["B02.scan"]["source"], "anchor")
        frames, report = self.run_map({"B02.scan": {"edge": "end"}}, {"B02.scan": 180}, self.hindi(),
                                      {"B02.scan": "poori table"})
        self.assertEqual(frames["B02.scan"], 238)      # end of "table"

    def test_relative_keeps_the_fraction_and_snaps_within_a_quarter_second(self):
        # English cue half way through B02 (frames 120..290); Hindi B02 is the same length
        frames, report = self.run_map({"B02.mid": {}}, {"B02.mid": 205}, self.hindi())
        self.assertEqual(report["cues"]["B02.mid"]["source"], "relative")
        self.assertEqual((frames["B02.mid"], report["cues"]["B02.mid"]["snapped"]), (210, True))
        # nothing within 7.5 frames: keep the raw fraction
        frames, report = self.run_map({"B02.mid": {}}, {"B02.mid": 195}, self.hindi())
        self.assertEqual((frames["B02.mid"], report["cues"]["B02.mid"]["snapped"]), (195, False))

    def test_a_pause_is_a_snap_point(self):
        frames, _ = self.run_map({"B02.mid": {}}, {"B02.mid": 158}, self.hindi(gap_after=5))  # pause starts at 154
        self.assertEqual(frames["B02.mid"], 154)

    def test_flags_ratio_anchor_and_collapsed_cues(self):
        hindi = self.hindi(step=12)
        frames, report = self.run_map(
            {"B02.a": {}, "B02.b": {}}, {"B02.a": 150, "B02.b": 158}, hindi,
            {"B02.a": "not said", "B02.zzz": "poori"})
        kinds = sorted(f["kind"] for f in report["flags"])
        self.assertEqual(kinds.count("anchor"), 2)       # unresolved phrase, and an unknown cue name
        self.assertIn("ratio", kinds)
        self.assertIn("close", kinds)
        self.assertIn("B02", report["flagged_beats"])
        self.assertTrue(report["still_frames"])
        self.assertEqual(report["beats"]["B02"]["ratio"] < 0.75, True)

    def test_cues_that_shared_a_frame_in_english_are_not_flagged(self):
        _, report = self.run_map({"B02.a": {}, "B02.b": {}}, {"B02.a": 150, "B02.b": 150}, self.hindi())
        self.assertNotIn("close", [f["kind"] for f in report["flags"]])

    def test_a_missing_beat_fails_the_cli_without_writing_frames(self):
        with tempfile.TemporaryDirectory() as td:
            en = os.path.join(td, "en")
            write_json(os.path.join(en, "cues.json"), {"B09.x": {"beat": "B09", "phrase": "x"}})
            write_json(os.path.join(en, "cue_frames.json"), {"B09.x": 10})
            write_json(os.path.join(en, "timeline.json"), self.EN)
            write_json(os.path.join(td, "data", "timeline.json"), self.hindi())
            write(os.path.join(td, "s.md"), "[B01 | HEAD] x\n")
            r = py("twin/map_cues.py", "--english-data", en, "--data", "data", "--script", "s.md", cwd=td, check=False)
            self.assertEqual(r.returncode, 1)
            self.assertFalse(os.path.exists(os.path.join(td, "data", "cue_frames.json")))
            self.assertEqual(read_json(os.path.join(td, "twin", "map-report.json"))["flags"][0]["kind"], "unmapped")


class TrailerTest(unittest.TestCase):
    WORDS = words(("B01", "a b"), ("B02", "c"), ("B03", "d e"), ("B04", "f"), step=30)

    def test_beat_lists(self):
        self.assertEqual(tr.parse_beat_list("B01, B02, B05–B07, B18 (+ any Hindi-only line changes)"),
                         ["B01", "B02", "B05", "B06", "B07", "B18"])

    def test_neighbouring_beats_merge_and_never_run_into_other_words(self):
        self.assertEqual(tr.ranges_for(self.WORDS, ["B01", "B02", "B04"], 200), [[0, 76], [146, 166]])
        with self.assertRaises(SystemExit):
            tr.ranges_for(self.WORDS, ["B09"], 200)

    def test_script_cut_else_the_english_trailer_beats(self):
        with tempfile.TemporaryDirectory() as td:
            w = World(td)
            self.assertEqual(tr.beats_in_ranges(w.en_words, [[0, 55], [75, 190]]), ["B01", "B03"])
            hindi = os.path.join(td, "tl.json")
            write_json(hindi, {"fps": 30, "total": 400, "words": words(("B01", "x y"), ("B02", "z"), ("B03", "p q"))})
            r = py("twin/trailer_ranges.py", "--script", os.path.join(w.twin, "script.md"), "--timeline", hindi,
                   "--out", "a.json", "--english-data", w.data, cwd=td)
            self.assertIn("60-second cut", r.stdout)
            write(os.path.join(td, "nocut.md"), "[B01 | HEAD] x\n")
            r = py("twin/trailer_ranges.py", "--script", "nocut.md", "--timeline", hindi, "--out", "b.json",
                   "--english-data", w.data, cwd=td)
            self.assertIn("the English trailer's beats", r.stdout)


class SetupRemotionTest(unittest.TestCase):
    def test_code_is_linked_data_is_own_and_english_stays_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            w = World(td)
            root = setup_remotion.setup(w.twin)
            for name in ("src", "scripts", "package.json", "node_modules"):
                self.assertTrue(os.path.islink(os.path.join(root, name)), name)
                self.assertFalse(os.path.isabs(os.readlink(os.path.join(root, name))))
            public = os.path.join(root, "public")
            for name in ("main.mp4", "voice.wav", "backdrop.jpg"):
                self.assertFalse(os.path.exists(os.path.join(public, name)), name)
            self.assertFalse(os.path.islink(os.path.join(public, "sfx", "pop.wav")))
            self.assertTrue(os.path.islink(os.path.join(public, "icons")))
            self.assertEqual(sorted(os.listdir(os.path.join(public, "data"))), ["cues.json", "slides.json"])
            # writing the twin's own files can't touch English
            write(os.path.join(public, "data", "slides.json"), "{}")
            write(os.path.join(public, "sfx", "pop.wav"), "hindi")
            with open(os.path.join(w.english, "work", "remotion", "public", "sfx", "pop.wav")) as f:
                self.assertEqual(f.read(), "pop")
            setup_remotion.setup(w.twin)                         # idempotent
            self.assertEqual(setup_remotion.verify(w.twin), [])
            write(os.path.join(root, "src", "plan.ts"), "edited through the link")
            self.assertEqual(setup_remotion.verify(w.twin), ["English src changed since setup: plan.ts"])

    def test_the_sfx_export_keeps_symlinks_unresolved(self):
        with open(os.path.join(REPO, "tools", "compose", "export_sfx.sh")) as f:
            self.assertIn("--preserve-symlinks", f.read())


class TwinValidatorTest(unittest.TestCase):
    SRT = "1\n00:00:00,000 --> 00:00:02,000\nchalo\n\n"

    def test_exactly_the_four_files(self):
        with tempfile.TemporaryDirectory() as td:
            w = World(td)
            setup_remotion.setup(w.twin)
            names = common.twin_deliverables(w.english)
            self.assertEqual(names, ["demo-video-hi_9x16.mp4", "demo-video-hi_9x16.srt",
                                     "demo-video-hi_trailer_9x16.mp4", "demo-video-hi_trailer_9x16.srt"])
            self.assertEqual({e["code"] for e in vt_validate.check_twin(w.twin)}, {"MISSING_DELIVERABLE"})
            for name in names:
                write(os.path.join(w.twin, "out", name), self.SRT if name.endswith(".srt") else "x")
            write(os.path.join(w.twin, "out", "roughcut_preview.mp4"), "x")
            self.assertEqual(vt_validate.check_twin(w.twin), [])
            for extra in ("demo-video-hi_social.json", "thumbnail/thumb_a.png", "carousel/01.png"):
                write(os.path.join(w.twin, "out", extra), "x")
            codes = [e["code"] for e in vt_validate.check_twin(w.twin)]
            self.assertEqual(codes, ["UNEXPECTED_DELIVERABLE"] * 3)
            r = py("validate/vt_validate.py", w.twin, "--check", "twin", cwd=td, check=False)
            self.assertEqual(r.returncode, 1)


def log_entry(minutes, cost, tokens):
    return (f"## 2026-01-05 10:0{minutes} IST · t\n\n**Finished** 10:0{minutes}:59 · **Took** {minutes} m 00 s\n**Stage:** deliver\n"
            f"**Tokens:** input {tokens} · cache write 0 · cache read 0 · output {tokens} (main session; subagents: none)\n"
            f"**Calls:** main {minutes} · sidechain 0 · subagents 0\n**Cost:** weighted USD {cost}\n\n")


class MetricsTest(unittest.TestCase):
    def test_records_carry_language_and_twin_of(self):
        with tempfile.TemporaryDirectory() as td:
            w = World(td)
            write(os.path.join(w.twin, "log.md"), log_entry(1, "0.5000", 10))
            record = stage_record.build_record(w.twin, "deliver")
            self.assertEqual((record["language"], record["twin_of"]), ("hi", "demo"))
            english = stage_record.build_record(w.english, "deliver")
            self.assertEqual((english["language"], english["twin_of"]), (None, None))

    def test_side_by_side(self):
        with tempfile.TemporaryDirectory() as td:
            for name, entry in (("en", log_entry(8, "4.0000", 100)), ("hi", log_entry(2, "1.0000", 20))):
                write(os.path.join(td, name, "log.md"), entry)
            result = json.loads(py("vt_log.py", "compare", os.path.join(td, "en"), os.path.join(td, "hi"),
                                   "--side-by-side", cwd=td).stdout)
        ratio = result["second_over_first"]
        self.assertEqual((ratio["cost_weighted_usd"], ratio["api_calls"], ratio["turn_seconds"]), (0.25, 0.25, 0.25))
        self.assertEqual(ratio["tokens"]["output"], 0.2)
        self.assertIsNone(vt_log.side_by_side("/nonexistent-a", "/nonexistent-b")["second_over_first"]["tokens"])


class CaptionReferenceTest(unittest.TestCase):
    TIMELINE = {"fps": 30, "words": [{"w": "chalo", "s": 0, "e": 15}, {"w": "50 crore", "s": 30, "e": 60},
                                     {"w": "", "s": 60, "e": 66}, {"w": "token", "s": 300, "e": 330}]}

    def test_shown_words_in_seconds_and_rebased_for_a_trailer(self):
        with tempfile.TemporaryDirectory() as td:
            write_json(os.path.join(td, "t.json"), self.TIMELINE)
            write_json(os.path.join(td, "r.json"), {"ranges": [[300, 360]]})
            full = caption_reference.load(os.path.join(td, "t.json"))
            self.assertEqual([w for *_, w in full], ["chalo", "50", "crore", "token"])
            self.assertEqual(caption_reference.load(os.path.join(td, "t.json"), os.path.join(td, "r.json")),
                             [[0.0, 1.0, "token"]])

    def test_video_inspect_takes_language_and_captions(self):
        with tempfile.TemporaryDirectory() as td:
            ffmpeg("-f", "lavfi", "-i", "testsrc2=s=180x320:r=30:d=2", "-f", "lavfi", "-i", "sine=d=2", "-shortest",
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(td, "v.mp4"))
            write_json(os.path.join(td, "t.json"), self.TIMELINE)
            py("inspect/video_inspect.py", "v.mp4", "--cpu-test", "--language", "hi", "--captions", "t.json", cwd=td)
            notes = read_json(os.path.join(td, "inspect", "v", "report.json"))["summary"]["notes"]
        self.assertIn("caption checks use t.json, not Whisper", notes)


class TwinDocsTest(unittest.TestCase):
    def test_the_skill_is_user_started_and_points_at_the_pipeline_and_house_numbers(self):
        with open(os.path.join(REPO, ".claude", "skills", "hindi-twin", "SKILL.md")) as f:
            skill = f.read()
        for needle in ("disable-model-invocation: true", "pipeline/hindi-twin.md", "House numbers", "stop for my OK"):
            self.assertIn(needle, skill)
        with open(os.path.join(REPO, "CLAUDE.md")) as f:
            self.assertEqual(sum("/hindi-twin" in line for line in f), 1)


if __name__ == "__main__":
    unittest.main()
