import json
import os
import tempfile
import unittest

from tools.hooks import transcript_ckpt as tck


class CheckpointValidationTest(unittest.TestCase):
    def test_rejects_boolean_offset(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "f.jsonl")
            with open(path, "wb") as f:
                f.write(b"x\n")
            st = os.stat(path)
            rec = {
                "offset": True,
                "identity": {"dev": st.st_dev, "ino": st.st_ino, "size": st.st_size, "mtime_ns": st.st_mtime_ns},
            }
            self.assertFalse(tck.validate_file_record(path, rec))

    def test_malformed_logged_ids_triggers_rescan(self):
        since = "2026-06-01T12:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "f.jsonl")
            with open(path, "w") as f:
                f.write(
                    json.dumps(
                        {
                            "type": "assistant",
                            "timestamp": since,
                            "message": {"id": "a1", "usage": {"input_tokens": 3, "output_tokens": 1}},
                        }
                    )
                    + "\n"
                )
            st = os.stat(path)
            ck = {
                "offset": st.st_size,
                "identity": {"dev": st.st_dev, "ino": st.st_ino, "size": st.st_size, "mtime_ns": st.st_mtime_ns},
                "logged_ids": {"not": "a_list"},
            }
            stats = {}
            start, _, ok = tck._resolve_start(path, ck, stats)
            self.assertFalse(ok)
            self.assertEqual(0, start)
            self.assertEqual(stats["mode"], "full_rescan")

    def test_wrong_session_marks_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            root = td
            sid = "wanted"
            p = tck.checkpoint_path(root, sid)
            with open(p, "w") as f:
                json.dump({"schema": 2, "session_id": "other", "files": {}}, f)
            ck = tck.load_checkpoint(root, sid)
            self.assertTrue(ck.get("_invalid"))

    def test_content_fp_mismatch_rescans(self):
        since = "2026-06-01T12:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "f.jsonl")
            line = (
                json.dumps(
                    {
                        "type": "assistant",
                        "timestamp": since,
                        "message": {"id": "m1", "usage": {"input_tokens": 5, "output_tokens": 1}},
                    }
                )
                + "\n"
            )
            with open(path, "w") as f:
                f.write(line)
            st = os.stat(path)
            off = st.st_size
            ck = {
                "offset": off,
                "identity": {"dev": st.st_dev, "ino": st.st_ino, "size": st.st_size, "mtime_ns": st.st_mtime_ns},
                "boundary_fp": tck._boundary_fingerprint(path, off),
                "content_fp": "deadbeef",
                "logged_ids": ["m1"],
            }
            with open(path, "r+") as f:
                f.seek(0)
                f.write(line.replace("5", "9"))
            st2 = os.stat(path)
            ck["identity"]["size"] = st2.st_size
            ck["offset"] = st2.st_size
            stats = {}
            start, _, ok = tck._resolve_start(path, ck, stats)
            self.assertFalse(ok)
            self.assertEqual(0, start)


    def test_truncation_rescans(self):
        since = "2026-06-01T12:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "f.jsonl")
            with open(path, "w") as f:
                f.write(
                    json.dumps(
                        {
                            "type": "assistant",
                            "timestamp": since,
                            "message": {"id": "t1", "usage": {"input_tokens": 1, "output_tokens": 1}},
                        }
                    )
                    + "\n"
                )
            st = os.stat(path)
            ck = {
                "offset": st.st_size,
                "identity": {"dev": st.st_dev, "ino": st.st_ino, "size": st.st_size, "mtime_ns": st.st_mtime_ns},
            }
            with open(path, "w") as f:
                f.write("\n")
            stats = {}
            _, _, ok = tck._resolve_start(path, ck, stats)
            self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()