import io
import json
import os
import tempfile
import threading
import unittest
from unittest import mock

from tools import asset_cache as ac
from tools.hooks import transcript_ckpt as tck
from tools.project_log_lock import project_log_lock


class HookConcurrencyTest(unittest.TestCase):
    def test_concurrent_asset_store_same_key(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            inp = os.path.join(proj, "in.bin")
            with open(inp, "wb") as f:
                f.write(b"same")
            errs = []

            def store_one(i):
                out = os.path.join(proj, f"out{i}.bin")
                with open(out, "wb") as f:
                    f.write(f"r{i}".encode())
                args = type(
                    "A",
                    (),
                    {
                        "project": proj,
                        "input": inp,
                        "op": "probe",
                        "params": "",
                        "output": out,
                        "script": None,
                        "tool_version": "1",
                    },
                )()
                try:
                    ac.cmd_store(args)
                except Exception as exc:
                    errs.append(exc)

            threads = [threading.Thread(target=store_one, args=(i,)) for i in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertFalse(errs, errs)
            man, err = ac._read_manifest_file(proj)
            self.assertIsNone(err)
            self.assertEqual(len(man["entries"]), 1)

    def test_project_log_lock_serializes(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            log = os.path.join(proj, "log.md")
            barrier = threading.Barrier(2)
            lengths = []

            def writer(tag):
                barrier.wait()
                with project_log_lock(proj):
                    with open(log, "a") as f:
                        f.write(f"{tag}\n")
                    with open(log) as f:
                        lengths.append(len(f.read()))

            t1 = threading.Thread(target=writer, args=("a",))
            t2 = threading.Thread(target=writer, args=("b",))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.assertEqual(min(lengths), 2)
            self.assertEqual(max(lengths), 4)


    def test_transcript_checkpoint_lock_serializes(self):
        with tempfile.TemporaryDirectory() as td:
            root = td
            sid = "sess"
            barrier = threading.Barrier(2)
            counters = []

            def one_pass():
                barrier.wait()
                with tck.checkpoint_lock(root, sid):
                    ck = tck.load_checkpoint(root, sid)
                    ck.setdefault("files", {})["_touch"] = ck.get("files", {}).get("_touch", 0) + 1
                    tck.save_checkpoint(root, sid, ck)

            t1 = threading.Thread(target=one_pass)
            t2 = threading.Thread(target=one_pass)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            ck = tck.load_checkpoint(root, sid)
            self.assertEqual(ck["files"]["_touch"], 2)


if __name__ == "__main__":
    unittest.main()