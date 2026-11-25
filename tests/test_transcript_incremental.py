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
            full_times = []
            inc_times = []
            for _ in range(5):
                t0 = time.perf_counter()
                rmain, rsub, _, _, _, _, _, _ = tck.collect_usage_reference(tp, [subf], since)
                full_times.append(time.perf_counter() - t0)
            ckpt = {"schema": 2, "session_id": "bench", "files": {}}
            seen: set[str] = set()
            st = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
            t0 = time.perf_counter()
            main, side, _, _, _, _, _, _ = tck.scan_parent_transcript(
                tp, since, seen, checkpoint=ckpt, session_id="bench", stats=st
            )
            sub, _, _, _, _ = tck.scan_subagent_files(
                [subf], since, seen, checkpoint=ckpt, session_id="bench", stats=st
            )
            for k in sub:
                sub[k] += side[k]
            inc_times.append(time.perf_counter() - t0)
            tck.save_checkpoint(td, "bench", ckpt)
            ckpt2 = tck.load_checkpoint(td, "bench")
            st2 = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
            seen2: set[str] = set()
            t1 = time.perf_counter()
            tck.scan_parent_transcript(tp, since, seen2, checkpoint=ckpt2, session_id="bench", stats=st2)
            inc_times.append(time.perf_counter() - t1)
            full_med = sorted(full_times)[len(full_times) // 2]
            inc_med = sorted(inc_times)[len(inc_times) // 2]
            inc_total = dict(main)
            for k in inc_total:
                inc_total[k] += sub[k]
            ref_total = dict(rmain)
            for k in ref_total:
                ref_total[k] += rsub[k]
            self.assertEqual(inc_total, ref_total)
            print(
                json.dumps(
                    {
                        "full_bytes": os.path.getsize(tp),
                        "incremental_first_bytes": st["bytes_read"],
                        "unchanged_pass_bytes": st2["bytes_read"],
                        "full_scan_median_s": round(full_med, 5),
                        "incremental_median_s": round(inc_med, 5),
                        "main_input": main["input"],
                        "sub_input": sub["input"],
                    },
                    indent=2,
                )
            )


if __name__ == "__main__":
    unittest.main()