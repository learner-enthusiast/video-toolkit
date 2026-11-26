"""Hindi caption engine with stubbed transliterator and aligner (CPU, no models)."""
import json
import os
import sys
import tempfile
import unittest

import numpy as np

from tests.tool_fixtures import REPO, py, read_json, speech_wav, tool, write, write_json
from tools.captions import hindi_numbers, hindi_text as ht
from tools.captions.align_mms import align_words, blank_id, forced_align

TABLES = hindi_numbers.load_tables()

# The model stub answers from a table and logs what it was asked.
TRANSLIT = '''import json, sys
TABLE = json.load(open(sys.argv[1], encoding="utf-8"))
words = json.load(open(sys.argv[2], encoding="utf-8"))
with open(sys.argv[1] + ".asked", "a", encoding="utf-8") as f:
    f.write("\\n".join(words) + "\\n")
json.dump({w: TABLE.get(w, []) for w in words}, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False)
'''
# The aligner stub gives word i the time 0.5*i .. 0.5*i+0.3 and cannot align digits.
ALIGN = '''import json, re, sys
words = json.load(open(sys.argv[1]))
json.dump([[0.5 * i, 0.5 * i + 0.3, 0.9] if re.search("[a-z]", w, re.I) else None for i, w in enumerate(words)],
          open(sys.argv[2], "w"))
'''
MODEL = {"चलो": ["chalo", "chello"], "आज": ["aaj"], "सीखेंगे": ["seekhenge"], "देखो": ["dekho"],
         "पोस्टग्रेस": ["postgres"], "तीन": ["teen"], "सौ": ["sau"], "रुपये": ["rupaye"], "यार": ["yaar"],
         "बहुत": ["bahut", "bohot"], "तेज़": ["tez"], "है": ["hai"], "यह": ["yah", "ye"]}


class Project:
    def __init__(self, td, script, heard, model=MODEL, dictionary=None):
        self.td = td
        self.work = os.path.join(td, "demo-hi", "work")
        os.makedirs(self.work)
        write(os.path.join(td, "demo-hi", "script.md"), script)
        # heard: [(word, start)] -> Whisper JSON
        write_json(os.path.join(self.work, "heard.json"), {"segments": [{"words": [
            {"word": " " + w, "start": s, "end": s + 0.3} for w, s in heard]}]})
        speech_wav(os.path.join(self.work, "voice.wav"), [(0.0, 0.3)], 20.0)
        write(os.path.join(td, "translit.py"), TRANSLIT)
        write(os.path.join(td, "align.py"), ALIGN)
        write_json(os.path.join(td, "model.json"), model)
        self.dictionary = os.path.join(td, "romanization.json")
        write_json(self.dictionary, dictionary or {})

    def run(self, *extra, check=True):
        return py("captions/hindi_captions.py", "--script", "../script.md", "--heard", "heard.json", "--wav", "voice.wav",
                  "--dictionary", self.dictionary,
                  "--translit-cmd", f"{sys.executable} {self.td}/translit.py {self.td}/model.json",
                  "--align-cmd", f"{sys.executable} {self.td}/align.py", *extra, cwd=self.work, check=check)

    def out(self, *parts):
        return os.path.join(self.work, *parts)

    def captions(self):
        with open(self.out("transcript", "caption_text.md"), encoding="utf-8") as f:
            return f.read()

    def report(self):
        return read_json(self.out("captions", "hi-report.json"))

    def words(self):
        return read_json(self.out("transcript", "words_aligned.json"))


def heard(text, start=0.0):
    return [(w, round(start + 0.4 * i, 2)) for i, w in enumerate(text.split())]


SCRIPT = '''# Demo

## Glossary (exact spellings for captions)
- PostgreSQL, Postgres

[B01 | HEAD] "chalo aaj Postgres sikhenge."
[B02 | SPLIT | price="teen sau"] teen sau rupaye
hai.

## 60-second cut
B01, B02
'''


class ScriptTextTest(unittest.TestCase):
    def test_spoken_lines_by_beat(self):
        self.assertEqual(ht.script_beats(SCRIPT),
                         [("B01", "chalo aaj Postgres sikhenge."), ("B02", "teen sau rupaye hai.")])
        template_style = '`[B03 | 00:05–00:11 | SPLIT]` · "line one" → show a card\n'
        self.assertEqual(ht.script_beats(template_style), [("B03", "line one")])

    def test_keys_tolerate_common_spellings(self):
        self.assertEqual(ht.key("Aaj"), ht.key("aj"))
        self.assertEqual(ht.key("wahan"), ht.key("vahaan"))
        self.assertNotEqual(ht.key("din"), ht.key("raat"))


class CaptionEngineTest(unittest.TestCase):
    def test_code_mixed_sentence_uses_my_spelling_and_passes_latin_through(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज Postgres सीखेंगे। तीन सौ रुपये है।"))
            p.run()
            report = p.report()
            self.assertEqual(p.captions(),
                             "### B01\nchalo aaj Postgres sikhenge.\n\n### B02\nteen sau rupaye hai.\n")
            counts = report["counts"]
            self.assertEqual((counts["matched"], counts["adlib"], counts["dropped"], counts["unknown"]), (8, 0, 0, 0))
            asked = open(os.path.join(td, "model.json.asked"), encoding="utf-8").read()
            self.assertNotIn("Postgres", asked)       # Latin words never go to the model

    def test_digits_from_whisper_match_spoken_numbers(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज पोस्टग्रेस सीखेंगे 300 रुपये है"))
            p.run()
            self.assertEqual(p.report()["counts"]["matched"], 8)
            self.assertIn("teen sau", p.captions())
            self.assertEqual(read_json(p.out("captions", "hi-display.json")), {"4": "₹300", "5": "", "6": ""})

    def test_adlib_and_dropped_words_are_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज Postgres देखो सीखेंगे तीन सौ रुपये"))   # +देखो, -hai
            p.run()
            report = p.report()
        flags = {(f["kind"], f["beat"], f["text"]) for f in report["flags"]}
        self.assertIn(("adlib", "B01", "dekho"), flags)
        self.assertIn(("dropped", "B02", "hai."), flags)
        self.assertEqual((report["counts"]["adlib"], report["counts"]["dropped"]), (1, 1))

    def test_dictionary_wins_over_the_model_for_adlibs(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज Postgres सीखेंगे यार तीन सौ रुपये है"),
                        model={**MODEL, "यार": ["yar"]},
                        dictionary={"यार": {"roman": "yaar", "count": 3, "last_project": "old"}})
            p.run()
            self.assertIn("yaar", p.captions())
            self.assertIn("from dictionary", p.report()["flags"][0]["detail"])

    def test_unknown_word_fails_and_writes_only_the_report(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज Postgres सीखेंगे ज़ोर तीन सौ रुपये है"))
            r = p.run(check=False)
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertEqual(p.report()["counts"]["unknown"], 1)
            self.assertFalse(os.path.exists(p.out("transcript", "caption_text.md")))

    def test_transliteration_never_changes_timestamps(self):
        results = []
        for spelling in ("dekho", "dekhho-different"):
            with tempfile.TemporaryDirectory() as td:
                p = Project(td, SCRIPT, heard("चलो आज Postgres देखो सीखेंगे तीन सौ रुपये है"),
                            model={**MODEL, "देखो": [spelling]})
                p.run()
                results.append(([w[:2] for w in p.words()], [w[2] for w in p.words()]))
        self.assertEqual(results[0][0], results[1][0])
        self.assertNotEqual(results[0][1], results[1][1])

    def test_summary_is_at_most_20_lines(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard(" ".join(["यार"] * 40)))
            out = p.run().stdout.strip().splitlines()
        self.assertLessEqual(len(out), 20)
        self.assertIn("more flag(s)", out[-1])


class LearnTest(unittest.TestCase):
    def test_matches_are_learned_sorted_with_count_and_project(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज Postgres सीखेंगे तीन सौ रुपये है"))
            p.run("--project", "demo-hi")
            learned = read_json(p.dictionary)
        self.assertEqual(list(learned), sorted(learned))
        self.assertEqual(learned["चलो"], {"roman": "chalo", "count": 1, "last_project": "demo-hi"})
        self.assertEqual(learned["सीखेंगे"]["roman"], "sikhenge")     # my spelling, not the model's
        self.assertNotIn("Postgres", learned)

    def test_no_learn_leaves_the_dictionary_alone(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज Postgres सीखेंगे तीन सौ रुपये है"))
            p.run("--no-learn")
            self.assertEqual(read_json(p.dictionary), {})
            self.assertTrue(p.report()["learned"])       # still reported

    def test_two_spellings_are_a_conflict_not_an_entry(self):
        dictionary = {"आज": {"roman": "aj", "count": 2, "last_project": "old"}}
        learned, conflicts = ht.learn(dictionary, [("आज", "aaj"), ("है", "hai"), ("है", "he")], "now")
        self.assertEqual(learned, [])
        self.assertEqual(dictionary, {"आज": {"roman": "aj", "count": 2, "last_project": "old"}})
        self.assertEqual({c["word"] for c in conflicts}, {"आज", "है"})


class NumberTest(unittest.TestCase):
    def shown(self, text):
        return [s for *_, s in hindi_numbers.display_runs(text.split(), TABLES)]

    def test_spoken_numbers_become_digits(self):
        for text, expected in (("teen sau", ["300"]), ("paanch hazaar do sau", ["5,200"]),
                               ("ek lakh aath hazaar rupaye", ["₹1,08,000"]), ("pachaas crore token", ["50 crore"]),
                               ("ek lakh", ["1 lakh"]), ("pachanve percent", ["95%"]), ("sau paanch", ["105"]),
                               ("do point paanch guna", ["2.5"]), ("do second", ["2"]), ("pachees", ["25"])):
            with self.subTest(text=text):
                self.assertEqual(self.shown(text), expected)

    def test_everyday_words_stay_words(self):
        for text in ("kar do", "ek developer", "teen baar", "do teen", "saath mein chalo"):
            with self.subTest(text=text):
                self.assertEqual(self.shown(text), [])


class EnginePipelineTest(unittest.TestCase):
    def test_build_timeline_and_srt_keep_the_english_formats(self):
        with tempfile.TemporaryDirectory() as td:
            p = Project(td, SCRIPT, heard("चलो आज Postgres सीखेंगे तीन सौ रुपये है"))
            p.run()
            write_json(p.out("edl.json"), {"segments": [[0, 5]]})
            write_json(p.out("config", "build_timeline.json"), {})
            os.makedirs(p.out("remotion", "public", "data"))
            py("captions/build_timeline.py", "transcript/words_aligned.json", "1.0",
               "--display", "captions/hi-display.json", cwd=p.work)
            tl = read_json(p.out("remotion", "public", "data", "timeline.json"))
            py("captions/make_srt.py", "--out", "out.srt", cwd=p.work)
            with open(p.out("out.srt"), encoding="utf-8") as f:
                srt = f.read()
            aligned = p.words()
        self.assertEqual([w["raw"] for w in tl["words"]], [w[2] for w in aligned])
        self.assertEqual([w["s"] for w in tl["words"]], [round(w[0] * 30) for w in aligned])
        self.assertIn("chalo aaj Postgres sikhenge.", srt)
        self.assertIn("₹300 hai.", srt)
        self.assertEqual([b["id"] for b in tl["beats"]], ["B01", "B02"])


class ForcedAlignTest(unittest.TestCase):
    def emissions(self, path, size=3):
        logp = np.log(np.full((len(path), size), 0.01))
        for t, label in enumerate(path):
            logp[t, label] = np.log(0.98)
        return logp

    def test_repeated_letters_need_a_blank_between_them(self):
        spans = forced_align(self.emissions([0, 1, 1, 0, 2, 0, 2, 2]), [1, 2, 2], blank=0)
        self.assertEqual([s[:2] for s in spans], [(1, 3), (4, 5), (6, 8)])

    def test_words_get_times_and_unalignable_words_get_none(self):
        out = align_words(self.emissions([0, 1, 1, 0, 2, 0, 2, 2]), ["A", "bb", "95%"], {"a": 1, "b": 2}, 0)
        self.assertEqual(out, [[0.02, 0.06, 0.98], [0.08, 0.16, 0.98], None])

    def test_the_blank_is_the_blank_token_not_the_pad_token(self):
        vocab = {"<blank>": 0, "<pad>": 1, "</s>": 2, "<unk>": 3, "a": 4}   # the real model's order
        self.assertEqual(blank_id(vocab), 0)
        with self.assertRaises(ValueError):
            blank_id({"<pad>": 1, "a": 4})

    def test_long_text_past_127_states(self):
        labels = [1, 2] * 150                       # 601 states: the backtrace index must not be int8
        path = [x for label in labels for x in (label, 0)]
        spans = forced_align(self.emissions(path), labels, blank=0)
        self.assertEqual([s[:2] for s in spans], [(2 * k, 2 * k + 1) for k in range(len(labels))])

    def test_text_longer_than_the_audio_fails(self):
        with self.assertRaises(ValueError):
            forced_align(self.emissions([1, 2]), [1, 2, 1, 2], blank=0)


class TrackedLanguageDataTest(unittest.TestCase):
    def test_dictionary_is_sorted_and_well_formed(self):
        data = read_json(os.path.join(REPO, "languages", "hi", "romanization.json"))
        self.assertEqual(list(data), sorted(data))
        for entry in data.values():
            self.assertEqual(set(entry), {"roman", "count", "last_project"})

    def test_transliteration_worker_never_handles_time(self):
        with open(tool("captions/xlit_worker.py"), encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn('"start"', source)
        self.assertNotIn("timestamp\"", source)


if __name__ == "__main__":
    unittest.main()
