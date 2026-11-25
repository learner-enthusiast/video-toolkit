import json
import os
import tempfile
import unittest

from tools.hooks import transcript_ckpt as tck


def _line(ts, mid, inp, sidechain=False, model="claude-sonnet-5-5"):
    return (
        json.dumps(
            {
                "type": "assistant",
                "timestamp": ts,
                "isSidechain": sidechain,
                "message": {
                    "id": mid,
                    "model": model,
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


class ParentSidechainAccountingTest(unittest.TestCase):
    """Regression for double-scan missing parent sidechain usage."""

    def test_main_sidechain_subagent_single_pass(self):
        since = "2026-06-01T12:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            parent = os.path.join(td, "t.jsonl")
            subdir = os.path.join(td, "subagents")
            os.makedirs(subdir)
            sub_path = os.path.join(subdir, "agent.jsonl")
            with open(parent, "w", encoding="utf-8") as f:
                f.write(_line(since, "A", 10, False))
                f.write(_line(since, "B", 20, True))
                f.write(_line(since, "C", 30, False))
                f.write(_line(since, "D", 40, True))
                f.write(_line(since, "E", 50, True))  # duplicate id in sub file
            with open(sub_path, "w", encoding="utf-8") as f:
                f.write(_line(since, "E", 50, False))
            seen: set[str] = set()
            stats = {}
            main, side, mm, sm, _, nm, ns, stats = tck.scan_parent_transcript(
                parent, since, seen, incremental=False, stats=stats
            )
            self.assertEqual(1, stats["parent_scans"])
            sub, subm, _, nsub, _ = tck.scan_subagent_files([sub_path], since, seen, incremental=False)
            for k in sub:
                sub[k] += side[k]
            self.assertEqual(main["input"], 10 + 30)  # A, C
            self.assertEqual(sub["input"], 20 + 40 + 50)  # B, D, E once
            self.assertEqual(150, main["input"] + sub["input"])
            ref_main, ref_sub, _, _, _, _, _, _ = tck.collect_usage_reference(parent, [sub_path], since)
            self.assertEqual(ref_main, main)
            self.assertEqual(ref_sub, sub)

    def test_old_double_scan_misses_sidechain(self):
        """Simulate PR #6 bug: second pass on parent with shared checkpoint skips sidechain."""
        since = "2026-06-01T12:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            parent = os.path.join(td, "t.jsonl")
            with open(parent, "w", encoding="utf-8") as f:
                f.write(_line(since, "A", 10, False))
                f.write(_line(since, "B", 20, True))
            ckpt = {"schema": 2, "session_id": "s", "files": {}}
            seen: set[str] = set()
            tck.usage_since([parent], since, main_only=True, seen=seen, checkpoint=ckpt, session_id="s")
            side_only, _, _, _ = tck.usage_since(
                [parent], since, main_only=False, seen=seen, checkpoint=ckpt, session_id="s"
            )
            self.assertEqual(side_only["input"], 0, "bug reproduction: sidechain lost on second pass")

    def test_parent_only_sidechain(self):
        since = "2026-06-01T12:00:00Z"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(_line(since, "B1", 7, True))
            f.write(_line(since, "B2", 8, True))
            path = f.name
        try:
            seen: set[str] = set()
            main, side, _, sm, _, nm, ns, _ = tck.scan_parent_transcript(path, since, seen, incremental=False)
            self.assertEqual(main["input"], 0)
            self.assertEqual(side["input"], 15)
            self.assertEqual(sm["claude-sonnet-5-5"]["input"], 15)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()