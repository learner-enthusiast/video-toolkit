import io
import json
import os
import sys
import tempfile
import threading
import unittest
from unittest import mock

_REPO = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _REPO)
from tools.hooks import projlog  # noqa: E402
from tools.hooks import transcript_ckpt as tck  # noqa: E402


def _assistant(ts, mid, inp, sidechain=False):
    return {
        "type": "assistant",
        "timestamp": ts,
        "isSidechain": sidechain,
        "message": {
            "id": mid,
            "model": "claude-sonnet-5-5",
            "usage": {
                "input_tokens": inp,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
                "output_tokens": 2,
            },
        },
    }


def _scaffold(root, sid, since, main_msgs=None, side_msgs=None, sub_msgs=None):
    os.makedirs(os.path.join(root, "projects", "demo", "work", "prompts"), exist_ok=True)
    os.makedirs(os.path.join(root, "projects", "demo", "work", "logs"), exist_ok=True)
    with open(os.path.join(root, "CLAUDE.md"), "w") as f:
        f.write("rules\n")
    with open(os.path.join(root, ".current-project"), "w") as f:
        f.write("projects/demo\n")
    prompt_ref = "work/prompts/2026-01-01_120000.md"
    with open(os.path.join(root, "projects", "demo", prompt_ref), "w") as f:
        f.write("hello\n")
    log_path = os.path.join(root, "projects", "demo", "log.md")
    with open(log_path, "w") as f:
        f.write(
            f"## 2026-01-01 12:00 IST · hello\n\n"
            f"**Prompt:** {prompt_ref}\n"
            f"**Started** 12:00:00\n\n"
        )
    st = {
        "prompt": "hello",
        "started_utc": since,
        "started_local": "2026-01-01T12:00:00+05:30",
        "mentioned": None,
        "project": "projects/demo",
        "prompt_ref": prompt_ref,
        "stage": "Prep",
    }
    os.makedirs(os.path.join(root, ".hook-state"), exist_ok=True)
    with open(os.path.join(root, ".hook-state", f"{sid}.json"), "w") as f:
        json.dump(st, f)
    tp = os.path.join(root, ".hook-state", f"{sid}.jsonl")
    subdir = os.path.join(root, ".hook-state", "subagents")
    os.makedirs(subdir, exist_ok=True)
    with open(tp, "w") as f:
        for m in main_msgs or []:
            f.write(json.dumps(m) + "\n")
        for m in side_msgs or []:
            f.write(json.dumps(m) + "\n")
    if sub_msgs:
        with open(os.path.join(subdir, "a.jsonl"), "w") as f:
            for m in sub_msgs:
                f.write(json.dumps(m) + "\n")
    return tp, log_path, prompt_ref


def _run_tokens(root, sid, tp):
    data = {"session_id": sid, "transcript_path": tp}
    os.environ["PROJLOG_NO_WAIT"] = "1"
    os.environ["PROJLOG_INCREMENTAL"] = "1"
    try:
        projlog.cmd_tokens(data, root)
    finally:
        os.environ.pop("PROJLOG_NO_WAIT", None)


class ProjlogStopTest(unittest.TestCase):
    def test_sidechain_only_reports_tokens(self):
        since = "2026-06-01T12:00:00Z"
        sid = "side-only"
        with tempfile.TemporaryDirectory() as td:
            tp, log_path, _ = _scaffold(
                td,
                sid,
                since,
                main_msgs=[],
                side_msgs=[_assistant(since, "s1", 42, True)],
            )
            _run_tokens(td, sid, tp)
            log = open(log_path).read()
            self.assertIn("**Tokens:**", log)
            self.assertNotIn("not available", log)
            self.assertIn("42", log)

    def test_duplicate_stop_leaves_footer(self):
        since = "2026-06-01T12:00:00Z"
        sid = "dup-stop"
        with tempfile.TemporaryDirectory() as td:
            tp, log_path, pref = _scaffold(
                td,
                sid,
                since,
                main_msgs=[_assistant(since, "m1", 11, False)],
            )
            state_path = os.path.join(td, ".hook-state", f"{sid}.json")
            _run_tokens(td, sid, tp)
            first = open(log_path).read()
            with open(state_path, "w") as f:
                json.dump(
                    {
                        "started_utc": since,
                        "project": "projects/demo",
                        "prompt_ref": pref,
                        "stage": "Prep",
                    },
                    f,
                )
            _run_tokens(td, sid, tp)
            second = open(log_path).read()
            self.assertEqual(first, second)
            self.assertEqual(1, second.count("**Tokens:**"))

    def test_concurrent_stop_hooks_one_footer(self):
        since = "2026-06-01T12:05:00Z"
        sid = "conc-stop"
        with tempfile.TemporaryDirectory() as td:
            tp, log_path, _ = _scaffold(
                td,
                sid,
                since,
                main_msgs=[_assistant(since, "m1", 20, False)],
            )
            barrier = threading.Barrier(2)
            errors = []

            def worker():
                try:
                    barrier.wait()
                    _run_tokens(td, sid, tp)
                except Exception as exc:
                    errors.append(exc)

            t1 = threading.Thread(target=worker)
            t2 = threading.Thread(target=worker)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.assertFalse(errors, errors)
            log = open(log_path).read()
            self.assertEqual(1, log.count("**Tokens:**"))
            self.assertIn("20", log)

    def test_checkpoint_save_failure_recovery(self):
        since = "2026-06-01T12:10:00Z"
        sid = "ckpt-fail"
        with tempfile.TemporaryDirectory() as td:
            tp, log_path, pref = _scaffold(
                td,
                sid,
                since,
                main_msgs=[_assistant(since, "m1", 15, False)],
            )
            state_path = os.path.join(td, ".hook-state", f"{sid}.json")
            with mock.patch.object(tck, "save_checkpoint", side_effect=OSError("disk")):
                _run_tokens(td, sid, tp)
            log1 = open(log_path).read()
            self.assertIn("15", log1)
            with open(state_path, "w") as f:
                json.dump(
                    {
                        "started_utc": since,
                        "project": "projects/demo",
                        "prompt_ref": pref,
                        "stage": "Prep",
                    },
                    f,
                )
            _run_tokens(td, sid, tp)
            log2 = open(log_path).read()
            self.assertIn("15", log2)
            self.assertNotIn("not available", log2)

    def test_new_prompt_not_same_as_prior_turn(self):
        since = "2026-06-01T12:00:00Z"
        since2 = "2026-06-01T13:00:00Z"
        sid = "two-turns"
        with tempfile.TemporaryDirectory() as td:
            tp, log_path, pref = _scaffold(
                td,
                sid,
                since,
                main_msgs=[_assistant(since, "a", 5, False)],
            )
            _run_tokens(td, sid, tp)
            pref2 = "work/prompts/2026-01-01_130000.md"
            with open(os.path.join(td, "projects", "demo", pref2), "w") as f:
                f.write("second\n")
            with open(log_path, "a") as f:
                f.write(
                    f"\n## 2026-01-01 13:00 IST · second\n\n"
                    f"**Prompt:** {pref2}\n"
                    f"**Started** 13:00:00\n\n"
                )
            with open(os.path.join(td, ".hook-state", f"{sid}.json"), "w") as f:
                json.dump(
                    {
                        "prompt": "second",
                        "started_utc": since2,
                        "started_local": "2026-01-01T13:00:00+05:30",
                        "project": "projects/demo",
                        "prompt_ref": pref2,
                        "stage": "Prep",
                    },
                    f,
                )
            with open(tp, "a") as f:
                f.write(json.dumps(_assistant(since2, "b", 8, False)) + "\n")
            _run_tokens(td, sid, tp)
            log = open(log_path).read()
            self.assertIn("**Tokens:**", log)
            self.assertEqual(2, log.count("**Tokens:**"))
            self.assertIn("8", log.split(pref2)[1])


if __name__ == "__main__":
    unittest.main()