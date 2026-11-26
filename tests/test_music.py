"""Music library, picking, mix and voice-safety checks, on synthetic audio. Only Whisper is stubbed."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import soundfile as sf

from tools import project_state as pst
from tools.hooks import read_guard
from tools.music import add_track, analyze, audition, finalize, house, library, pick, restore
from tools.qa import clarity, loudness_windows as lw, voice_over_music as vom
from tools.sound import music_bed

ROOT = Path(__file__).resolve().parents[1]
SR = 48000


def beat_track(bpm=120, bars=12, drone=0.05):
    """A bar that repeats: four different hits over a steady low tone."""
    beat = 60 / bpm
    x = np.zeros(int(SR * beat * 4 * bars))
    for b in range(4 * bars):
        i, n = int(b * beat * SR), int(0.12 * SR)
        t = np.arange(n) / SR
        noise = np.random.default_rng(b % 4).normal(0, 1, n)
        x[i:i + n] += 0.4 * np.sin(2 * np.pi * (220, 330, 262, 392)[b % 4] * t) * np.exp(-30 * t) \
            + 0.15 * noise * np.exp(-80 * t)
    return x + drone * np.sin(2 * np.pi * 110 * np.arange(len(x)) / SR)


def speech(words=10, word_s=0.9, pause_s=0.3, start_s=1.0, tail_s=4.0):
    """Speech-like noise bursts with the pauses between my words. Returns (samples, spans)."""
    spans = [[start_s + i * (word_s + pause_s), start_s + i * (word_s + pause_s) + word_s] for i in range(words)]
    x = np.zeros(int((spans[-1][1] + tail_s) * SR))
    rng = np.random.default_rng(3)
    for a, b in spans:
        i, n = int(a * SR), int((b - a) * SR)
        x[i:i + n] = 0.2 * np.sin(np.linspace(0, np.pi, n)) ** 0.3 * rng.normal(0, 1, n)
    return x, spans


def quiet(func, *args, **kwargs):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        result = func(*args, **kwargs)
    return result, out.getvalue()


class LibraryCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.lib = self.tmp / "music"
        self.lib.mkdir()
        header = (ROOT / "music" / "index.md").read_text().split("|---")[0]
        rule = "|" + "---|" * len(library.COLUMNS)
        (self.lib / "index.md").write_text(header + rule + "\n")
        patcher = mock.patch.dict(os.environ, {"VT_MUSIC_DIR": str(self.lib)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.proof = self.tmp / "license.pdf"
        self.proof.write_bytes(b"%PDF license")

    def wav(self, name, samples):
        path = self.tmp / name
        sf.write(path, samples, SR, subtype="PCM_24")
        return str(path)

    def add(self, name="calm-one", samples=None, *flags, url="https://uppbeat.io/t/x", licensed=True):
        path = self.wav(f"{name}.wav", beat_track() if samples is None else samples)
        argv = [path, "--source-url", url, "--license-type", "Uppbeat Premium", "--mood", "calm,tech"]
        if licensed:
            argv += ["--license-file", str(self.proof)]
        argv += flags or ("--instrumental",)
        return add_track.add(add_track.parser().parse_args(argv))

    def entry(self, track_id, last_used=library.EMPTY, house_track=True, length="200.0 s", loopable="no"):
        row = dict.fromkeys(library.COLUMNS, library.EMPTY)
        row.update(id=track_id, file=f"{track_id}.wav", length=length, loopable=loopable, instrumental="yes",
                   credit="none", last_used=last_used, **{"★house": "★" if house_track else library.EMPTY})
        library.write(library.rows() + [row])

    def project(self, name="demo", **state):
        path = self.tmp / "projects" / name
        (path / "work").mkdir(parents=True)
        (path / "out").mkdir()
        (path / "log.md").write_text(f"# {name} log\n")
        st = pst.default_state(str(path))
        st.update(state)
        pst.save_state(str(path), st)
        return path


class AddTrackTest(LibraryCase):
    def test_refuses_without_license_or_instrumental_or_from_a_rip(self):
        for kwargs, word in (({"licensed": False}, "license"), ({"url": "https://youtu.be/abc"}, "not a licensed"),
                             ({"url": "https://open.spotify.com/track/1"}, "not a licensed")):
            with self.assertRaisesRegex(SystemExit, word):
                self.add("a", None, "--instrumental", **kwargs)
        with self.assertRaisesRegex(SystemExit, "--instrumental"):
            self.add("a", None, "--house")
        with self.assertRaisesRegex(SystemExit, "instrumental"):
            self.add("a", None, "--allow-vocals", "--house")
        self.assertEqual(library.rows(), [])
        self.assertFalse((self.lib / "tracks").exists())

    def test_row_is_measured_sorted_and_hashed(self):
        self.add("zeta")
        row = self.add("alpha", beat_track(drone=0.08), "--instrumental", "--house",
                       url="https://pixabay.com/music/x")
        self.assertEqual([r["id"] for r in library.rows()], ["alpha", "zeta"])
        self.assertEqual(library.find("alpha"), row)
        self.assertEqual(row["sha256"], library.sha256(str(self.lib / "tracks" / "alpha.wav")))
        self.assertAlmostEqual(float(row["bpm"]), 120, delta=0.5)
        self.assertEqual(library.seconds(row), 24.0)
        start, seam = library.loop_points(row)
        self.assertAlmostEqual((seam - start) % 2.0, 0, delta=0.01)     # whole bars
        self.assertEqual(row["content_id_risk"], "known risk")
        self.assertTrue((self.lib / "licenses" / "alpha.pdf").is_file())
        lufs, peak = (float(v) for v in row["LUFS / TP"].split(" / "))
        self.assertTrue(-60 < lufs < 0 and -40 < peak <= 3)
        with self.assertRaisesRegex(SystemExit, "already"):
            self.add("alpha")

    def test_a_drone_has_no_tempo_and_is_not_loopable(self):
        row = self.add("drone", 0.1 * np.sin(2 * np.pi * 110 * np.arange(SR * 10) / SR))
        self.assertEqual((row["bpm"], row["loopable"]), (library.EMPTY, "no"))

    def test_restore_lists_missing_and_changed(self):
        self.add("keep")
        self.add("gone", beat_track(drone=0.07), url="https://uppbeat.io/t/gone")
        self.assertEqual(restore.problems(), [])
        (self.lib / "tracks" / "gone.wav").unlink()
        (self.lib / "tracks" / "keep.wav").write_bytes(b"other")
        code, out = quiet(restore.main)
        self.assertEqual(code, 1)
        self.assertIn("gone: missing", out)
        self.assertIn("https://uppbeat.io/t/gone", out)
        self.assertIn("keep: sha256 differs", out)


class PickTest(LibraryCase):
    def test_prompt_line(self):
        self.assertEqual(pick.prompt_value("**Music:** lofi-01 \n"), "lofi-01")
        self.assertEqual(pick.prompt_value("**Notes:** x\n"), "")
        self.assertEqual(pick.prompt_value("**Music:** <id | none>\n"), "")
        self.assertIn("**Music:**", (ROOT / "templates" / "editing-prompt.md").read_text())

    def test_modes(self):
        self.assertEqual(pick.resolve("", 100)["mode"], "no-house-track")
        self.entry("b-new", last_used="2026-11-20")
        self.entry("c-never")
        self.entry("a-old", last_used="2026-10-01")
        self.entry("d-short", length="60.0 s")
        self.entry("e-loops", length="30.0 s", loopable="yes @ 28.000 s from 0.000 s", last_used="2026-09-01")
        self.entry("f-plain", house_track=False)
        self.assertEqual([r["id"] for r in pick.rotation(170)], ["c-never", "e-loops", "a-old", "b-new"])
        self.assertEqual(pick.resolve("", 170), {"id": "c-never", "mode": "rotation"})
        self.assertEqual(pick.resolve("", 45)["id"], "c-never")
        self.assertEqual(pick.resolve("none", 170), {"id": None, "mode": "none"})
        self.assertEqual(pick.resolve("f-plain", 170), {"id": "f-plain", "mode": "named"})
        self.assertEqual(pick.resolve("music/tracks/a-old.wav", 170)["id"], "a-old")
        self.assertEqual(pick.resolve("audition [b-new, f-plain]", 170)["candidates"], ["b-new", "f-plain"])
        self.assertEqual(pick.resolve("audition", 170)["candidates"], ["c-never", "e-loops", "a-old"])
        with self.assertRaises(SystemExit):
            pick.resolve("nope", 170)

    def test_record_twin_inherits_and_log_restores_it(self):
        self.entry("one")
        english = self.project("demo")
        twin = self.project("demo-hi", twin_of="demo", language="hi")
        quiet(pick.main, [str(english), "--value", "one"])
        quiet(pick.main, [str(twin), "--value", "none"])              # the twin's own line is ignored
        music = pst.load_state(str(twin))["music"]
        self.assertEqual((music["id"], music["mode"]), ("one", "inherited"))
        self.assertIn("**Music bed:** one (named)", (english / "log.md").read_text())
        os.remove(pst.state_path(str(english)))
        self.assertEqual(pst.sync_handoff(str(english))["music"], {"id": "one", "mode": "named"})

    def test_set_music_takes_the_audition_number(self):
        self.entry("one")
        project = self.project()
        (project / "out" / "music-audition").mkdir()
        (project / "out" / "music-audition" / "audition.json").write_text(json.dumps(
            {"tracks": [{"n": 1, "id": "x", "status": "rejected", "reason": "gap"}, {"n": 2, "id": "one", "status": "ok"}]}))
        quiet(pst.cmd_set_music, mock.Mock(project=str(project), choice="2"))
        self.assertEqual(pst.load_state(str(project))["music"]["id"], "one")
        with self.assertRaises(SystemExit):
            pst.cmd_set_music(mock.Mock(project=str(project), choice="1"))
        quiet(pst.cmd_set_music, mock.Mock(project=str(project), choice="none"))
        self.assertIsNone(pst.load_state(str(project))["music"]["id"])


class BedTest(unittest.TestCase):
    def setUp(self):
        self.params = music_bed.settings()
        self.voice, self.spans = speech()
        self.noise = 0.2 * np.random.default_rng(7).normal(0, 1, len(self.voice))

    def test_values_come_from_house_numbers(self):
        text = (ROOT / "CLAUDE.md").read_text()
        self.assertEqual((self.params["gap_target_db"], self.params["gap_fail_db"], self.params["fade_in_s"]), (20, 15, 1.5))
        self.assertIn("20 dB under my voice (fail < 15 dB)", text)
        config = json.loads((ROOT / "config" / "music.json").read_text())
        self.assertFalse({"gap_target_db", "gap_fail_db", "fade_in_s"} & set(config))
        with self.assertRaises(SystemExit):
            music_bed.settings({"hold_s": 0.2})

    def test_loop_crossfade_has_no_click(self):
        track = 0.3 * np.sin(2 * np.pi * 220.3 * np.arange(SR * 6) / SR)       # not periodic at the seam
        bed, seams = music_bed.fit(track, SR * 17, (0.5, 4.5), 0.25)
        self.assertEqual(len(bed), SR * 17)
        self.assertEqual(seams[0], 4.5)
        self.assertLess(np.abs(np.diff(bed)).max(), 1.5 * np.abs(np.diff(track)).max())
        with self.assertRaisesRegex(SystemExit, "not loopable"):
            music_bed.fit(track, SR * 17, None, 0.25)
        self.assertEqual(music_bed.fit(track, SR * 2, None, 0.25)[1], [])

    def test_duck_holds_through_my_pauses_and_rises_only_in_real_gaps(self):
        gain = music_bed.duck_gain_db(self.voice, self.params)
        for (_, end), (start, _) in zip(self.spans, self.spans[1:]):
            self.assertAlmostEqual(start - end, 0.3, places=6)
            self.assertEqual(gain[int(end * SR): int(start * SR)].max(), 0.0)
        self.assertAlmostEqual(gain[int((self.spans[-1][1] + 2.5) * SR)], self.params["duck_depth_db"], places=3)
        self.assertAlmostEqual(gain[0], self.params["duck_depth_db"], delta=0.2)       # before the hook
        self.assertEqual(gain[int((self.spans[0][0] + 0.05) * SR)], 0.0)             # already down

    def test_gap_measurement_within_1_db(self):
        tone = 0.2 * np.sin(2 * np.pi * 997 * np.arange(len(self.voice)) / SR)
        for wanted in (6, 20, 27):
            measured = lw.gap(tone, tone * 10 ** (-wanted / 20), self.spans, self.params)
            self.assertAlmostEqual(measured["median_db"], wanted, delta=1)
            self.assertAlmostEqual(measured["worst_db"], wanted, delta=1)
        # only speaking windows count: loud music in a real gap changes nothing
        music = tone * 0.1
        music[int((self.spans[-1][1] + 1) * SR):] *= 20
        self.assertAlmostEqual(lw.gap(tone, music, self.spans, self.params)["worst_db"], 20, delta=1)

    def test_a_too_loud_stretch_is_lowered_until_it_passes_and_the_voice_is_untouched(self):
        music = self.noise.copy()
        music[int(6 * SR): int(8 * SR)] *= 4                    # 12 dB louder: 8 dB under the voice at first
        before = self.voice.copy()
        first, _ = music_bed.build(self.voice, self.spans, music, None, {**self.params, "auto_level_rounds": 0})
        self.assertLess(lw.gap(self.voice, first, self.spans, self.params)["worst_db"], 15)
        bed, report = music_bed.build(self.voice, self.spans, music, None, self.params)
        self.assertTrue(report["passed"])
        self.assertGreaterEqual(report["auto_level_rounds"], 1)
        self.assertGreaterEqual(lw.gap(self.voice, bed, self.spans, self.params)["worst_db"], 15)
        np.testing.assert_array_equal(self.voice, before)

    def test_steady_music_lands_on_the_target_and_fades(self):
        bed, report = music_bed.build(self.voice, self.spans, self.noise, None, self.params)
        self.assertAlmostEqual(report["gap"]["median_db"], 20, delta=0.5)
        self.assertEqual(bed[0], 0.0)
        self.assertLess(abs(bed[-1]), 1e-6)
        self.assertGreater(np.std(bed[-SR * 3:-SR * 2]), 0)           # still playing after my last word


def fake_whisper(voice, mix=None, controls=None, mix_again=None):
    """Whisper stub: what it "hears" depends on which WAV it is given. Times shift with the audio."""
    def transcribe(project, wav, out_dir, language):
        name = os.path.basename(wav)
        later = clarity.LATER_S if name.endswith("_later.wav") else 0.0
        mixed = name.startswith(("final_", "mix_"))
        if mixed:
            heard = (mix_again if later and mix_again is not None else mix)
        else:
            heard = (controls if controls is not None and name.endswith(("_later.wav", "_quieter.wav")) else voice)
        heard = voice if heard is None else heard
        return [[s + later, e + later, w] for s, e, w in heard]
    return transcribe


class ClarityTest(unittest.TestCase):
    def run_check(self, **heard):
        voice = [[0.0, 0.4, "alpha"], [1.0, 1.4, "bravo"], [2.0, 2.4, "charlie"]]
        with tempfile.TemporaryDirectory() as td:
            for name in ("voice.wav", "mix_a.wav"):
                sf.write(os.path.join(td, name), np.zeros(SR), SR)
            with mock.patch.object(clarity, "transcribe", fake_whisper(voice, **heard)) :
                return clarity.check(td, os.path.join(td, "voice.wav"), os.path.join(td, "mix_a.wav"), td, "en")

    def test_only_words_whisper_hears_reliably_can_block(self):
        voice = [[0.0, 0.4, "alpha"], [1.0, 1.4, "bravo"], [2.0, 2.4, "charlie"]]
        without = lambda *drop: [w for w in voice if w[2] not in drop]
        masked = self.run_check(mix=without("bravo"))
        self.assertEqual((masked["passed"], [w["word"] for w in masked["missing"]]), (False, ["bravo"]))
        shaky = self.run_check(mix=without("bravo"), controls=without("bravo"))
        self.assertEqual((shaky["passed"], shaky["testable_words"], shaky["voice_words"]), (True, 2, 3))
        once = self.run_check(mix=without("charlie"), mix_again=voice)
        self.assertTrue(once["passed"])

    def test_variants_are_inaudible_changes(self):
        with tempfile.TemporaryDirectory() as td:
            sf.write(os.path.join(td, "v.wav"), 0.5 * np.ones(SR), SR, subtype="PCM_24")
            quieter, _ = sf.read(clarity.variant(os.path.join(td, "v.wav"), "quieter", td))
            later, _ = sf.read(clarity.variant(os.path.join(td, "v.wav"), "later", td))
        self.assertAlmostEqual(20 * np.log10(quieter[0] / 0.5), -0.5, places=3)
        self.assertEqual((len(later), later[0], later[-1]), (SR + 2400, 0.0, 0.5))

    def test_flags_a_masked_word_and_ignores_spelling(self):
        voice = [[0.0, 0.4, " Redis"], [0.5, 0.9, "is"], [1.0, 1.4, "an"], [1.5, 1.9, "in-memory"],
                 [2.0, 2.4, "store."], [2.5, 2.9, "Every"], [3.0, 3.3, "one"], [3.4, 3.8, "colour"]]
        heard = [[0.0, 0.4, "redis"], [0.5, 0.9, "is"], [1.5, 1.9, "in memory"], [2.0, 2.4, "store"],
                 [2.5, 3.3, "everyone"], [3.4, 3.8, "color"]]
        self.assertEqual(clarity.missing_words(voice, heard), [{"at_s": 1.0, "word": "an"}])
        changed = clarity.missing_words(voice[:5], [[0.0, 0.4, "reddit"], *voice[1:4], [2.0, 2.4, "shore"]])
        self.assertEqual([w["word"] for w in changed], [" Redis", "store."])       # reddit, shore
        self.assertEqual(clarity.token("कैसे!"), "कैसे")               # vowel signs stay

    def test_a_number_is_the_same_word_however_whisper_writes_it(self):
        timed = lambda text: [[i, i + 0.4, w] for i, w in enumerate(text.split())]
        for said, heard in (("cost you three times", "cost you 3 times"), ("तीन गुना", "३ गुना"), ("तीन गुना", "3 गुना")):
            self.assertEqual(clarity.missing_words(timed(said), timed(heard)), [], said)
        self.assertEqual(clarity.missing_words(timed("twenty three"), [[0, 1.4, "23"]]), [])
        self.assertEqual([w["word"] for w in clarity.missing_words(timed("cost you three"), timed("cost you 8"))],
                         ["three"])

    def test_reads_both_transcript_shapes(self):
        with tempfile.TemporaryDirectory() as td:
            whisper, inspect = Path(td, "a.json"), Path(td, "report.json")
            whisper.write_text(json.dumps({"segments": [{"words": [{"start": 0, "end": 1, "word": " hi"}]}]}))
            inspect.write_text(json.dumps({"words": [[0, 1, "hi"]]}))
            self.assertEqual(clarity.words(str(whisper)), clarity.words(str(inspect)))
        self.assertIn("--vad_filter", clarity.FLAGS)
        self.assertIn("vad_filter=True", (ROOT / "tools" / "inspect" / "video_inspect.py").read_text())


class DeliverableTest(LibraryCase):
    """The real chain on a synthetic project: mix.py, music_bed.py, mix.py --music, then the checks."""

    def build_project(self, choice):
        project = self.project()
        work = project / "work"
        voice, self.spans = speech()
        for folder in ("audio", "remotion/public/data", "remotion/public/sfx"):
            (work / folder).mkdir(parents=True, exist_ok=True)
        sf.write(work / "audio" / "voice.wav", voice, SR, subtype="PCM_24")
        sf.write(work / "remotion" / "public" / "sfx" / "pop.wav",
                 0.1 * np.sin(2 * np.pi * 660 * np.arange(SR // 10) / SR), SR, subtype="PCM_24")
        (work / "audio" / "sfx_cues.json").write_text(json.dumps(
            {"duration": len(voice) / SR, "cues": [{"sound": "pop", "t": 2.0, "gain_db": -6}]}))
        words = [{"w": f"word{i}", "s": a * 30, "e": b * 30} for i, (a, b) in enumerate(self.spans)]
        (work / "remotion" / "public" / "data" / "timeline.json").write_text(json.dumps(
            {"fps": 30, "words": words, "beats": [{"id": "B01", "words": [0, 4]}, {"id": "B02", "words": [5, 9]}]}))
        if choice is not None:
            quiet(pick.record, str(project), choice)
        return project

    def tool(self, work, *argv):
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        return subprocess.run([sys.executable, *argv], cwd=work, env=env, capture_output=True, text=True)

    def mix(self, work, *extra):
        done = self.tool(work, str(ROOT / "tools" / "compose" / "mix.py"), "main", *extra)
        self.assertEqual(done.returncode, 0, done.stderr)
        return (work / "audio" / "mix.wav").read_bytes()

    def test_no_music_leaves_the_mix_byte_identical(self):
        project = self.build_project({"id": None, "mode": "none"})
        work = project / "work"
        plain = self.mix(work)
        done = self.tool(work, str(ROOT / "tools" / "sound" / "music_bed.py"), "main")
        self.assertEqual(done.returncode, 3, done.stderr)
        self.assertFalse((work / "audio" / "stems").exists())
        self.assertEqual((work / "audio" / "mix.wav").read_bytes(), plain)
        # the mix of a video without music is still voice + SFX and the 0.5 s fade, nothing else
        dur = json.loads((work / "audio" / "sfx_cues.json").read_text())["duration"]
        reference = work / "audio" / "reference.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(work / "audio" / "voice_main.wav"), "-i",
                        str(work / "audio" / "sfx.wav"), "-filter_complex",
                        f"[0][1]amix=inputs=2:normalize=0,afade=t=out:st={dur - 0.5:.3f}:d=0.5[o]", "-map", "[o]",
                        "-ar", "48000", "-c:a", "pcm_s24le", str(reference)], check=True)
        self.assertEqual(reference.read_bytes(), plain)

    def deliver(self):
        self.add("bed", beat_track(), "--instrumental", "--house", "--credit", "Music: Bed by A (CC BY 4.0)")
        project = self.build_project({"id": "bed", "mode": "named"})
        work = project / "work"
        self.mix(work)
        voice_before = (work / "audio" / "voice_main.wav").read_bytes()
        done = self.tool(work, str(ROOT / "tools" / "sound" / "music_bed.py"), "main")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.mix(work, "--music", "audio/stems/main-music.wav")
        self.assertEqual((work / "audio" / "voice_main.wav").read_bytes(), voice_before)
        final = project / "out" / "demo_9x16.wav"
        gain = house.values()["lufs"] - analyze.loudness(str(work / "audio" / "mix.wav"))[0]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(work / "audio" / "mix.wav"), "-af",
                        f"volume={gain}dB,alimiter=limit=0.8:level=false", "-ar", "48000", str(final)], check=True)
        return project, work, str(final)

    def test_full_chain_then_checks_then_blockers(self):
        project, work, final = self.deliver()
        used = json.loads((work / "config" / "sound_music.json").read_text())
        self.assertEqual(used["track"]["id"], "bed")
        self.assertEqual(used["params"]["gap_target_db"], 20)
        self.assertEqual(used["deliverables"]["main"]["loops_at_s"], [])   # 24 s of music, 16.9 s of video
        said = [[a, b, f"word{i}"] for i, (a, b) in enumerate(self.spans)]
        with mock.patch.object(clarity, "transcribe", return_value=said) as whisper:
            report = vom.run(str(project), final)
        self.assertTrue(report["passed"], vom.summary_line("main", report))
        self.assertGreaterEqual(report["gap"]["worst_db"], 15)
        self.assertIn(report["gap"]["worst_beat"], ("B01", "B02"))
        self.assertEqual(whisper.call_count, 4)          # voice, its two controls, the mix
        self.assertIn("**Music QA:** main PASS", (project / "log.md").read_text())

        masked = [w for w in said if w[2] != "word4"]
        with mock.patch.object(clarity, "transcribe", fake_whisper(said, mix=masked)):
            report = vom.run(str(project), final)
        self.assertFalse(report["passed"])
        self.assertEqual(report["clarity"]["missing"][0]["word"], "word4")

        # the inspect transcript of this render saves the second Whisper pass
        transcript = work / "inspect.json"
        transcript.write_text(json.dumps({"words": said}))
        with mock.patch.object(clarity, "transcribe", return_value=said) as whisper:
            self.assertTrue(vom.run(str(project), final, str(transcript))["passed"])
        self.assertEqual(whisper.call_count, 3)          # no second pass over the render

        # a stem made 12 dB louder after the bed was built is stale, not silently accepted
        stem, _ = sf.read(work / "audio" / "stems" / "main-music.wav")
        sf.write(work / "audio" / "stems" / "main-music.wav", stem * 4, SR, subtype="PCM_24")
        gap = vom.check_gap(str(work), "main", library.find("bed"))
        self.assertFalse(gap["passed"])
        self.assertIn("changed", gap["problem"])

    def test_twin_reuses_the_english_mix_values(self):
        english = self.project("demo")
        twin = self.project("demo-hi", twin_of="demo", language="hi")
        with self.assertRaisesRegex(SystemExit, "English"):
            music_bed.twin_params(str(twin))
        (english / "work" / "config").mkdir()
        values = {**music_bed.settings(), "duck_depth_db": 4.5}
        (english / "work" / "config" / "sound_music.json").write_text(json.dumps({"params": values}))
        self.assertEqual(music_bed.settings(music_bed.twin_params(str(twin)))["duck_depth_db"], 4.5)
        self.assertIsNone(music_bed.twin_params(str(english)))

    def test_trailer_words_come_from_the_trailer_ranges(self):
        project = self.build_project(None)
        work = project / "work"
        (work / "audio" / "trailer_ranges.json").write_text(json.dumps({"ranges": [[150, 225]]}))
        spans = music_bed.word_spans(str(work / "remotion/public/data/timeline.json"),
                                     str(work / "audio/trailer_ranges.json"))
        self.assertEqual(spans, [[0.8, 1.7], [2.0, 2.5]])     # words 4 and 5 on the trailer clock, the last clipped
        self.assertEqual(vom.beat_label(str(work / "remotion/public/data/timeline.json"), 1.0,
                                        str(work / "audio/trailer_ranges.json")), "B01")


class AuditionTest(LibraryCase):
    def test_refuses_before_the_rough_cut_then_writes_previews(self):
        self.add("good", beat_track(), "--instrumental", "--house")
        self.add("short", 0.1 * np.random.default_rng(1).normal(0, 1, SR * 4), "--instrumental", "--house")
        project = self.project()
        work = project / "work"
        with self.assertRaisesRegex(SystemExit, "voice gate"):
            audition.run(str(project), None)
        (work / "audio" / "cleaned").mkdir(parents=True)
        voice, spans = speech(words=24, tail_s=2.0)
        sf.write(work / "audio" / "cleaned" / "recording-01.wav", voice, SR)
        with self.assertRaisesRegex(SystemExit, "rough cut"):
            audition.run(str(project), None)
        sf.write(work / "audio" / "voice.wav", voice, SR, subtype="PCM_24")
        with self.assertRaisesRegex(SystemExit, "word timings"):
            audition.run(str(project), None)
        (work / "transcript" / "cut").mkdir(parents=True)
        (work / "transcript" / "cut" / "voice.json").write_text(json.dumps(
            {"segments": [{"words": [{"start": a, "end": b, "word": f"w{i}"} for i, (a, b) in enumerate(spans)]}]}))
        said = [[0, 1, "hello"]]
        with mock.patch.object(clarity, "transcribe", return_value=said):
            results, out = quiet(audition.run, str(project), ["good", "short"])
        self.assertEqual([r["status"] for r in results], ["ok", "rejected"])
        self.assertIn("not loopable", results[1]["reason"])
        folder = project / "out" / "music-audition" / "01-good"
        self.assertEqual(sorted(p.name for p in folder.iterdir()),
                         ["voice_only.wav", "with_music.wav", "with_music_phone.wav"])
        self.assertFalse((project / "out" / "music-audition" / "02-short").exists())
        report = (project / "out" / "music-audition" / "report.md").read_text()
        self.assertRegex(report, r"1 · good · voice over music median 20 dB, worst \d+ dB · clarity PASS")
        self.assertIn("2 · short · REJECTED", report)
        with mock.patch.object(clarity, "transcribe", fake_whisper(said, mix=[])):
            results, _ = quiet(audition.run, str(project), ["good"])
        self.assertIn("clarity", results[0]["reason"])

    def test_windows_are_the_busiest_stretch_and_the_longest_pause(self):
        words = [[t, t + 0.4, "a"] for t in (0, 3, 6)] + [[40 + i * 0.5, 40.4 + i * 0.5, "b"] for i in range(30)] \
            + [[70, 70.4, "c"]]
        params = music_bed.settings()["audition"]
        busy, calm = audition.windows(words, 75.0, params)
        self.assertEqual(busy[:2], ("busiest", 40))
        self.assertEqual(calm[0], "longest pause")
        self.assertTrue(calm[1] < 23 < calm[2])
        self.assertEqual(audition.windows([[0, 0.4, "a"], [0.5, 0.9, "b"]], 30.0, params)[1][:2], ("hook", 0.0))


class BookkeepingTest(LibraryCase):
    def test_credit_reaches_the_social_json_and_the_track_is_marked_used(self):
        line = "Music: Bed by A (CC BY 4.0)"
        self.entry("bed")
        rows = library.rows()
        rows[0]["credit"] = line
        library.write(rows)
        project = self.project(music={"id": "bed", "mode": "named"})
        social = {"youtube": {"title": "T", "description": "About."}, "linkedin": {"post": "Post"},
                  "x": {"post": "x" * 270, "post_long": None}, "threads": {"post": ""}}
        path = project / "out" / "demo_social.json"
        path.write_text(json.dumps(social))
        _, out = quiet(finalize.finalize, str(project), "2026-11-26")
        _, again = quiet(finalize.finalize, str(project), "2026-11-27")
        after = json.loads(path.read_text())
        self.assertEqual(after["youtube"]["description"], f"About.\n\n{line}")
        self.assertEqual(after["linkedin"]["post"].count(line), 1)
        self.assertEqual(after["x"]["post"], "x" * 270)
        self.assertIn("DOES NOT FIT in x.post", out)
        row = library.find("bed")
        self.assertEqual((row["used_in"], row["last_used"]), ("demo", "2026-11-26"))

    def test_read_guard(self):
        root = self.tmp
        (root / "music" / "tracks").mkdir()
        for name in ("a.mp3", "a.m4a", "a.flac"):
            self.assertIsNotNone(read_guard.blocked_reason(f"music/tracks/{name}", str(root)))
        self.assertIsNone(read_guard.blocked_reason("music/index.md", str(root)))
        (root / "music" / "index.md").write_text("row\n" * 60)
        self.assertIsNotNone(read_guard.blocked_reason("music/index.md", str(root)))
        self.assertIsNone(read_guard.blocked_reason("music/index.md", str(root), limit=20))

    def test_audio_is_ignored_by_git(self):
        done = subprocess.run(["git", "check-ignore", "-q", "music/tracks/x.mp3"], cwd=ROOT)
        self.assertEqual(done.returncode, 0)
        done = subprocess.run(["git", "check-ignore", "-q", "music/licenses/x.pdf"], cwd=ROOT)
        self.assertEqual(done.returncode, 1)


if __name__ == "__main__":
    unittest.main()
