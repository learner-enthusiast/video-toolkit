import json
import os
import tempfile
import time
import unittest

from tools.hooks import transcript_ckpt as tck


def _assistant_line(ts, mid, inp, sidechain=False):
    return (
        json.dumps(
            {
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
                        "output_tokens": 1,
                    },
                },
            }
        )
        + "\n"
    )


class TranscriptIncrementalTest(unittest.TestCase):
    def _history(self, path, n_hist: int):
        with open(path, "ab") as f:
            for i in range(n_hist):
                f.write(_assistant_line("2020-01-01T00:00:00Z", f"hist-{i}", 1).encode())

    def test_equivalent_to_full_scan(self):
        since = "2026-06-01T12:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            tp = os.path.join(td, "t.jsonl")
            open(tp, "wb").close()
            self._history(tp, 200)
            with open(tp, "ab") as f:
                f.write(_assistant_line(since, "new-1", 40).encode())
                f.write(_assistant_line(since, "new-2", 5, True).encode())
            ref_main, ref_sub, _, _, _, _, _, _ = tck.collect_usage_reference(tp, [], since)
            ckpt = {"schema": 2, "session_id": "s1", "files": {}}
            seen: set[str] = set()
            st = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
            main, side, _, _, _, _, _, _ = tck.scan_parent_transcript(
                tp, since, seen, checkpoint=ckpt, session_id="s1", stats=st
            )
            sub = dict(side)
            inc_total = dict(main)
            for k in inc_total:
                inc_total[k] += sub[k]
            ref_total = dict(ref_main)
            for k in ref_total:
                ref_total[k] += ref_sub[k]
            self.assertEqual(inc_total, ref_total)

    def _bench_pass(self, tp, subf, since, ckpt, root):
        seen: set[str] = set()
        st = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
        t0 = time.perf_counter()
        main, side, mm, sm, _, _, _, _ = tck.scan_parent_transcript(
            tp, since, seen, checkpoint=ckpt, session_id=ckpt["session_id"], stats=st
        )
        sub, subm, _, _, _ = tck.scan_subagent_files(
            [subf], since, seen, checkpoint=ckpt, session_id=ckpt["session_id"], stats=st
        )
        dt_s = time.perf_counter() - t0
        sub_combined = dict(sub)
        for k in sub_combined:
            sub_combined[k] += side[k]
        if root and ckpt is not None:
            tck.save_checkpoint(root, ckpt["session_id"], ckpt)
        return {
            "bytes_read": st["bytes_read"],
            "records_scanned": st["records_scanned"],
            "records_parsed": st["records_parsed"],
            "main_input": main["input"],
            "sub_input": sub_combined["input"],
            "runtime_s": dt_s,
            "main_models": mm,
            "sub_models": {**sm, **subm},
        }

    def test_benchmark_table(self):
        since = "2026-06-01T12:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            tp = os.path.join(td, "t.jsonl")
            open(tp, "wb").close()
            self._history(tp, 500)
            subdir = os.path.join(td, "subagents")
            os.makedirs(subdir)
            subf = os.path.join(subdir, "a.jsonl")
            with open(tp, "ab") as f:
                f.write(_assistant_line(since, "m1", 100).encode())
                f.write(_assistant_line(since, "s1", 25, True).encode())
            with open(subf, "wb") as f:
                f.write(_assistant_line(since, "sa", 10).encode())
            full_runs = []
            for _ in range(5):
                t0 = time.perf_counter()
                rmain, rsub, rmm, rsm, _, _, _, _ = tck.collect_usage_reference(tp, [subf], since)
                full_runs.append(
                    {
                        "runtime_s": time.perf_counter() - t0,
                        "bytes_read": os.path.getsize(tp) + os.path.getsize(subf),
                        "main_input": rmain["input"],
                        "sub_input": rsub["input"],
                    }
                )
            ckpt = tck.load_checkpoint(td, "bench")
            init = self._bench_pass(tp, subf, since, ckpt, td)
            self.assertEqual(init["main_input"], rmain["input"])
            self.assertEqual(init["sub_input"], rsub["input"])

            ckpt_u = tck.load_checkpoint(td, "bench")
            stu = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
            t0 = time.perf_counter()
            tck.scan_parent_transcript(tp, since, set(), checkpoint=ckpt_u, session_id="bench", stats=stu)
            tck.scan_subagent_files([subf], since, set(), checkpoint=ckpt_u, session_id="bench", stats=stu)
            unchanged = {
                "bytes_read": stu["bytes_read"],
                "runtime_s": time.perf_counter() - t0,
                "main_input": init["main_input"],
                "sub_input": init["sub_input"],
            }

            with open(tp, "ab") as f:
                f.write(_assistant_line(since, "m2", 3).encode())
            with open(subf, "ab") as f:
                f.write(_assistant_line(since, "sb", 4).encode())
            ckpt_a = tck.load_checkpoint(td, "bench")
            append = self._bench_pass(tp, subf, since, ckpt_a, td)
            ref_after, rsub_after, _, _, _, _, _, _ = tck.collect_usage_reference(tp, [subf], since)
            self.assertEqual(ref_after["input"], rmain["input"] + 3)
            self.assertEqual(rsub_after["input"], rsub["input"] + 4)
            self.assertEqual(append["main_input"], 3)
            self.assertGreaterEqual(append["sub_input"], 4)

            def med(xs):
                ys = sorted(xs)
                return ys[len(ys) // 2]

            report = {
                "A_full_scan_median_s": round(med([r["runtime_s"] for r in full_runs]), 5),
                "B_initial_incremental": {k: init[k] for k in ("bytes_read", "runtime_s", "main_input", "sub_input")},
                "C_append_incremental": {k: append[k] for k in ("bytes_read", "runtime_s", "main_input", "sub_input")},
                "D_unchanged_pass": unchanged,
            }
            print(json.dumps(report, indent=2))


if __name__ == "__main__":
    unittest.main()