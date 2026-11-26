import json
import os
import tempfile
import unittest

from tools.hooks import transcript_ckpt as tck


def _line(ts, mid, inp, sidechain=False):
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


class CrossFileDedupTest(unittest.TestCase):
    """Message IDs must dedupe across hook executions and transcript files."""

    def test_parent_then_subagent_two_executions(self):
        since = "2026-06-01T12:00:00Z"
        sid = "sess-dedup-a"
        with tempfile.TemporaryDirectory() as td:
            root = td
            parent = os.path.join(td, "t.jsonl")
            subdir = os.path.join(td, "subagents")
            os.makedirs(subdir)
            sub_path = os.path.join(subdir, "a.jsonl")
            with open(parent, "w", encoding="utf-8") as f:
                f.write(_line(since, "X", 100, False))
            ckpt = tck.load_checkpoint(root, sid)
            seen: set[str] = set()
            main, side, _, _, _, _, _, _ = tck.scan_parent_transcript(
                parent, since, seen, checkpoint=ckpt, session_id=sid
            )
            self.assertEqual(main["input"], 100)
            tck.save_checkpoint(root, sid, ckpt)

            with open(sub_path, "w", encoding="utf-8") as f:
                f.write(_line(since, "X", 100, False))
            ckpt2 = tck.load_checkpoint(root, sid)
            seen2: set[str] = set()
            sub, _, _, nsub, _ = tck.scan_subagent_files(
                [sub_path], since, seen2, checkpoint=ckpt2, session_id=sid
            )
            self.assertEqual(nsub, 0)
            self.assertEqual(sub["input"], 0)
            self.assertEqual(main["input"] + sub["input"], 100)

    def test_subagent_then_parent_two_executions(self):
        since = "2026-06-01T12:00:00Z"
        sid = "sess-dedup-b"
        with tempfile.TemporaryDirectory() as td:
            root = td
            parent = os.path.join(td, "t.jsonl")
            subdir = os.path.join(td, "subagents")
            os.makedirs(subdir)
            sub_path = os.path.join(subdir, "a.jsonl")
            with open(sub_path, "w", encoding="utf-8") as f:
                f.write(_line(since, "Y", 77, False))
            ckpt = tck.load_checkpoint(root, sid)
            seen: set[str] = set()
            sub, _, _, nsub, _ = tck.scan_subagent_files(
                [sub_path], since, seen, checkpoint=ckpt, session_id=sid
            )
            self.assertEqual(sub["input"], 77)
            tck.save_checkpoint(root, sid, ckpt)

            with open(parent, "w", encoding="utf-8") as f:
                f.write(_line(since, "Y", 77, False))
            ckpt2 = tck.load_checkpoint(root, sid)
            seen2: set[str] = set()
            main, side, _, _, _, nm, ns, _ = tck.scan_parent_transcript(
                parent, since, seen2, checkpoint=ckpt2, session_id=sid
            )
            self.assertEqual(nm, 0)
            self.assertEqual(main["input"], 0)
            self.assertEqual(sub["input"], 77)


if __name__ == "__main__":
    unittest.main()