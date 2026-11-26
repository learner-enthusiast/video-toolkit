"""Job runner, delivery shell tools and the small helpers. GPU and network commands are stubbed."""
import array
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import wave

from tests.tool_fixtures import REPO, TOOLS, ffmpeg, run, tool, write, write_json


def status(jobs, job):
    with open(os.path.join(jobs, f"{job}.status")) as f:
        return f.read()


class BatchTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.work = os.path.join(self.td.name, "work")
        self.jobs = os.path.join(self.work, "jobs")
        os.makedirs(self.jobs)

    def tearDown(self):
        self.td.cleanup()

    def batch(self, text):
        write(os.path.join(self.jobs, "t.batch"), text)
        return run(["bash", tool("jobs/batch.sh"), os.path.join(self.jobs, "t.batch")], cwd=self.td.name, check=False)

    def test_jobs_run_one_at_a_time_in_order_from_work(self):
        r = self.batch("# comment\n"
                       "01-a | 20 | a.txt | echo a-start >> order; sleep 0.4; echo a-end >> order\n"
                       "\n"
                       "02-b | 20 | b.txt | echo b >> order; printf 'x\\ny\\n' | grep -c .\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(os.path.join(self.work, "order")) as f:
            self.assertEqual(f.read().split(), ["a-start", "a-end", "b"])
        self.assertRegex(status(self.jobs, "02-b"), r"state=done\nexit=0\nseconds=\d+\noutput=b.txt\nlog_tail<<\n2\n")
        self.assertIn("BATCH DONE 2 job(s)", r.stdout)

    def test_first_failure_stops_the_batch(self):
        r = self.batch("01-a | 20 | - | false | true\n02-b | 20 | - | touch ran\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("state=failed", status(self.jobs, "01-a"))   # pipefail: a broken pipe stage fails the job
        self.assertFalse(os.path.exists(os.path.join(self.work, "ran")))
        self.assertFalse(os.path.exists(os.path.join(self.jobs, "02-b.status")))

    def test_per_job_timeout(self):
        r = self.batch("01-slow | 1 | - | sleep 20\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("exit=124", status(self.jobs, "01-slow"))

    def test_bad_file_runs_nothing(self):
        for bad in ("02-b | soon | - | true", "02-b | 20 | - ", "01-a | 20 | - | true", "../x | 20 | - | true"):
            with self.subTest(bad=bad):
                r = self.batch(f"01-a | 20 | - | touch ran\n{bad}\n")
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertFalse(os.path.exists(os.path.join(self.work, "ran")))

    def test_stale_status_is_removed(self):
        write(os.path.join(self.jobs, "02-b.status"), "state=done\n")
        self.batch("01-a | 20 | - | false\n02-b | 20 | - | true\n")
        self.assertFalse(os.path.exists(os.path.join(self.jobs, "02-b.status")))

    def test_second_batch_is_refused_while_one_runs(self):
        write(os.path.join(self.jobs, "t.batch"), "01-a | 20 | - | touch started; sleep 3\n")
        first = subprocess.Popen(["bash", tool("jobs/batch.sh"), os.path.join(self.jobs, "t.batch")], stdout=subprocess.DEVNULL)
        try:
            deadline = time.time() + 10
            while not os.path.exists(os.path.join(self.work, "started")) and time.time() < deadline:
                time.sleep(0.05)
            r = run(["bash", tool("jobs/batch.sh"), os.path.join(self.jobs, "t.batch")], check=False)
            self.assertEqual(r.returncode, 3, r.stderr)
        finally:
            self.assertEqual(first.wait(timeout=20), 0)

    def test_job_report_reads_the_status(self):
        self.batch("01-a | 20 | out.bin | echo hello\n")
        r = run([sys.executable, tool("job_report.py"), os.path.join(self.jobs, "01-a.status")])
        self.assertIn('"status": "done"', r.stdout)


class ShellDeliveryTest(unittest.TestCase):
    def stubs(self, td):
        """gpu-run records its arguments; for an encode or render it writes a tiny output file."""
        bin_ = os.path.join(td, "bin")
        write(os.path.join(bin_, "gpu-run"), f'''#!/bin/bash
echo "$*" >> "{td}/gpu.log"
case "$1" in
  vt-python) exit 0 ;;
  npx) out=$6 ;;
  *) out="${{@: -1}}" ;;
esac
ffmpeg -hide_banner -loglevel error -y -f lavfi -i color=s=64x64:d=1 -f lavfi -i sine=d=1 -shortest "$out"
''', executable=True)
        for name in ("curl", "nvidia-smi", "sleep"):
            write(os.path.join(bin_, name), "#!/bin/bash\nexit 0\n", executable=True)
        return {"PATH": bin_ + os.pathsep + os.environ["PATH"]}

    def log(self, td):
        with open(os.path.join(td, "gpu.log")) as f:
            return f.read()

    def test_render_chain_uses_the_config_and_unchanged_settings(self):
        with tempfile.TemporaryDirectory() as td:
            env = self.stubs(td)
            work = os.path.join(td, "work")
            os.makedirs(os.path.join(work, "remotion"))
            os.makedirs(os.path.join(work, "audio"))
            ffmpeg("-f", "lavfi", "-i", "sine=d=2", os.path.join(work, "audio", "mix.wav"))
            write_json(os.path.join(work, "config", "render_chain.json"),
                       {"outputs": {"Main": {"name": "demo_9x16", "mix": "audio/mix.wav"}}})
            r = run(["bash", tool("jobs/render_chain.sh")], cwd=work, env=env)
            gpu = self.log(td)
            self.assertTrue(os.path.isfile(os.path.join(td, "out", "demo_9x16.mp4")))
            bad = run(["bash", tool("jobs/render_chain.sh"), "Nope"], cwd=work, env=env, check=False)
        self.assertIn("DECODE_CHECK Main done", r.stdout)
        for setting in ("--codec=prores", "--gl=angle", "--concurrency=3", "-c:v h264_nvenc -preset p6 -tune hq -rc vbr -cq 19",
                        "alimiter=limit=0.69:level=false,loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=", "linear=true"):
            self.assertIn(setting, gpu)
        self.assertEqual(bad.returncode, 2)

    def test_qa_inspect_is_thorough_on_the_first_video_only(self):
        with tempfile.TemporaryDirectory() as td:
            env = self.stubs(td)
            for name in ("main_9x16.mp4", "main_trailer_9x16.mp4"):
                ffmpeg("-f", "lavfi", "-i", "color=s=108x192:d=6:r=5", os.path.join(td, name))
            r = run(["bash", tool("qa/qa_inspect.sh"), "main_9x16.mp4", "main_trailer_9x16.mp4"], cwd=td, env=env)
            calls = [c for c in self.log(td).splitlines() if "video_inspect.py" in c]
            self.assertTrue(os.path.isfile(os.path.join(td, "inspect", "main_9x16", "sheet_01.jpg")))
        self.assertIn(f"{TOOLS}/inspect/video_inspect.py main_9x16.mp4 --thorough", calls[0])
        self.assertNotIn("--thorough", calls[1])
        self.assertIn("EXIT sheets main_trailer_9x16 0", r.stdout)

    def test_gpu_wait_runs_the_command(self):
        with tempfile.TemporaryDirectory() as td:
            r = run(["bash", tool("jobs/gpu_wait.sh"), "echo", "ran"], env=self.stubs(td))
        self.assertIn("ran", r.stdout)


class SoundKitTest(unittest.TestCase):
    def test_kit_builds_ten_sounds_near_minus_3_dbfs(self):
        with tempfile.TemporaryDirectory() as td:
            run(["bash", tool("sound/build_kit.sh"), td])
            names = sorted(os.listdir(td))
            self.assertEqual(len(names), 10, names)
            for name in names:
                with wave.open(os.path.join(td, name)) as w:
                    self.assertEqual((w.getframerate(), w.getnchannels()), (48000, 1), name)
                    samples = array.array("h", w.readframes(w.getnframes()))
                peak = max(abs(s) for s in samples) / 32768
                # Wider than the doc's ±0.1 dB: filter output varies between FFmpeg versions.
                self.assertTrue(0.62 < peak < 0.80, f"{name} peak {peak:.3f}")


class OcrToolTest(unittest.TestCase):
    def test_ocr_output_shape(self):
        with tempfile.TemporaryDirectory() as td:
            ffmpeg("-f", "lavfi", "-i", "color=s=100x200:d=1", "-frames:v", "1", os.path.join(td, "f.png"))
            write(os.path.join(td, "stubs", "paddleocr.py"), '''
class PaddleOCR:
    def __init__(s, **kw): pass
    def predict(s, p): return [{"rec_texts": ["Hi", "faint"], "rec_scores": [0.99, 0.2], "rec_boxes": [[10, 20, 50, 40], [0, 0, 1, 1]]}]
''')
            write(os.path.join(td, "stubs", "PIL", "__init__.py"), "")
            write(os.path.join(td, "stubs", "PIL", "Image.py"),
                  "class _I:\n    size = (100, 200)\ndef open(p): return _I()\n")
            write_json(os.path.join(td, "list.json"), ["f.png"])
            run([sys.executable, tool("inspect/video_inspect_ocr.py"), "list.json", "out.json"], cwd=td,
                env={"PYTHONPATH": os.path.join(td, "stubs")})
            with open(os.path.join(td, "out.json")) as f:
                self.assertEqual(f.read(), '{"f.png": [["Hi", 0.99, [0.1, 0.1, 0.5, 0.2]]]}')


class NoVideoSpecificValuesTest(unittest.TestCase):
    def test_tools_name_no_project(self):
        pattern = re.compile(r"prompt.?caching|system-design-of-ai|sdai|jensen|tokenizers|cost-metering|semantic-caching", re.I)
        hits = []
        for folder, _, files in os.walk(os.path.join(REPO, "tools")):
            for name in files:
                if name.endswith((".py", ".sh")):
                    with open(os.path.join(folder, name)) as f:
                        hits += [f"{name}: {line.strip()}" for line in f if pattern.search(line)]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
