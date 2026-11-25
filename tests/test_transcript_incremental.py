import json
import os
import tempfile
import time
import unittest

from tools.hooks import transcript_ckpt as tck


def _assistant_line(ts: str, mid: str, inp: int, sidechain: bool = False) -> bytes:
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
    ).encode()


class TranscriptIncrementalTest(unittest.TestCase):
    def _make_large(self, path: str, n_hist: int):
        with open(path, "wb") as f:
            for i in range(n_hist):
                f.write(_assistant_line("2020-01-01T00:00:00Z", f"hist-{i}", 1))

    def test_equivalent_to_full_scan(self):
        with tempfile.TemporaryDirectory() as td:
            tp = os.path.join(td, "t.jsonl")
            self._make_large(tp, 200)
            with open(tp, "ab") as f:
                f.write(_assistant_line("2026-06-01T12:00:00Z", "new-1", 40))
                f.write(_assistant_line("2026-06-01T12:00:01Z", "new-2", 5))
            since = "2026-06-01T12:00:00Z"
            ckpt = {"schema": 1, "session_id": "s1", "files": {}}
            st_inc = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
            inc, _, _, _ = tck.usage_since(
                [tp], since, main_only=True, checkpoint=ckpt, session_id="s1", stats=st_inc
            )
            full, _, _, _ = tck.usage_since_full([tp], since, main_only=True)
            self.assertEqual(inc, full)
            tck.save_checkpoint(td, "s1", ckpt)
            ckpt2 = tck.load_checkpoint(td, "s1")
            with open(tp, "ab") as f:
                f.write(_assistant_line("2026-06-01T12:01:00Z", "new-3", 7, False))
            since2 = "2026-06-01T12:01:00Z"
            st2 = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
            inc2, _, _, _ = tck.usage_since(
                [tp], since2, main_only=True, checkpoint=ckpt2, session_id="s1", stats=st2
            )
            self.assertEqual(inc2["input"], 7)
            self.assertLess(st2["bytes_read"], os.path.getsize(tp) // 2)

    def test_shared_seen_dedupes(self):
        with tempfile.TemporaryDirectory() as td:
            tp = os.path.join(td, "t.jsonl")
            with open(tp, "wb") as f:
                f.write(_assistant_line("2026-06-01T12:00:00Z", "dup-id", 10))
            since = "2026-06-01T12:00:00Z"
            seen = set()
            a, _, n1, _ = tck.usage_since_full([tp], since, main_only=True, seen=seen)
            b, _, n2, _ = tck.usage_since_full([tp], since, main_only=True, seen=seen)
            self.assertEqual(n1, 1)
            self.assertEqual(n2, 0)
            self.assertEqual(b["input"], 0)
            self.assertEqual(a["input"], 10)

    def test_benchmark_table(self):
        with tempfile.TemporaryDirectory() as td:
            tp = os.path.join(td, "t.jsonl")
            self._make_large(tp, 500)
            with open(tp, "ab") as f:
                f.write(_assistant_line("2026-06-01T12:00:00Z", "bench-1", 100))
            since = "2026-06-01T12:00:00Z"
            ckpt = {"schema": 1, "session_id": "bench", "files": {}}
            st_inc = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0, "mode": ""}
            t0 = time.perf_counter()
            inc, _, _, _ = tck.usage_since(
                [tp], since, main_only=True, checkpoint=ckpt, session_id="bench", stats=st_inc
            )
            t_inc = time.perf_counter() - t0
            t1 = time.perf_counter()
            full, _, _, _ = tck.usage_since_full([tp], since, main_only=True)
            t_full = time.perf_counter() - t1
            self.assertEqual(inc, full)
            # second pass incremental after checkpoint
            tck.save_checkpoint(td, "bench", ckpt)
            ckpt = tck.load_checkpoint(td, "bench")
            st2 = {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
            t2 = time.perf_counter()
            tck.usage_since([tp], since, main_only=True, checkpoint=ckpt, session_id="bench", stats=st2)
            t_ckpt = time.perf_counter() - t2
            self.assertLess(st2["bytes_read"], st_inc["bytes_read"])
            print(
                json.dumps(
                    {
                        "full_bytes_read": os.path.getsize(tp),
                        "incremental_first_bytes": st_inc["bytes_read"],
                        "checkpoint_pass_bytes": st2["bytes_read"],
                        "full_seconds": round(t_full, 4),
                        "incremental_first_seconds": round(t_inc, 4),
                        "checkpoint_pass_seconds": round(t_ckpt, 4),
                        "tokens_match": inc == full,
                    },
                    indent=2,
                )
            )


if __name__ == "__main__":
    unittest.main()