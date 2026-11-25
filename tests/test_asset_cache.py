import io
import json
import os
import tempfile
import unittest
from unittest import mock

from tools import asset_cache as ac


class AssetCacheTest(unittest.TestCase):
    def test_store_and_lookup_hit(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            inp = os.path.join(proj, "in.bin")
            out = os.path.join(proj, "out.bin")
            with open(inp, "wb") as f:
                f.write(b"data")
            with open(out, "wb") as f:
                f.write(b"result")
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
                    "tool_version": "1.0",
                },
            )()
            ac.cmd_store(args)
            lookup = type(
                "A",
                (),
                {
                    "project": proj,
                    "input": inp,
                    "op": "probe",
                    "params": "",
                    "script": None,
                    "tool_version": "1.0",
                },
            )()
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit) as e:
                    ac.cmd_lookup(lookup)
            self.assertEqual(e.exception.code, 0)
            self.assertTrue(json.loads(buf.getvalue())["hit"])

    def test_changed_input_misses(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            inp = os.path.join(proj, "in.bin")
            out = os.path.join(proj, "out.bin")
            with open(inp, "wb") as f:
                f.write(b"data")
            with open(out, "wb") as f:
                f.write(b"result")
            store = type(
                "A",
                (),
                {
                    "project": proj,
                    "input": inp,
                    "op": "probe",
                    "params": "",
                    "output": out,
                    "script": None,
                    "tool_version": "",
                },
            )()
            ac.cmd_store(store)
            with open(inp, "wb") as f:
                f.write(b"data-changed")
            lookup = type(
                "A",
                (),
                {
                    "project": proj,
                    "input": inp,
                    "op": "probe",
                    "params": "",
                    "script": None,
                    "tool_version": "",
                },
            )()
            with mock.patch("sys.stdout", io.StringIO()):
                with self.assertRaises(SystemExit) as e:
                    ac.cmd_lookup(lookup)
            self.assertEqual(e.exception.code, 1)

    def test_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            inp = os.path.join(proj, "in.bin")
            out = os.path.join(proj, "out.bin")
            with open(inp, "wb") as f:
                f.write(b"data")
            with open(out, "wb") as f:
                f.write(b"result")
            store = type(
                "A",
                (),
                {
                    "project": proj,
                    "input": inp,
                    "op": "probe",
                    "params": "",
                    "output": out,
                    "script": None,
                    "tool_version": "",
                },
            )()
            ac.cmd_store(store)
            key = ac.cache_key("probe", inp, None, tool_version="unknown")
            path = os.path.join(ac.bundle_root(proj, key), "out.bin")
            with open(path, "wb") as f:
                f.write(b"tampered")
            lookup = type(
                "A",
                (),
                {
                    "project": proj,
                    "input": inp,
                    "op": "probe",
                    "params": "",
                    "script": None,
                    "tool_version": "",
                },
            )()
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit) as e:
                    ac.cmd_lookup(lookup)
            self.assertEqual(e.exception.code, 1)
            self.assertIn(json.loads(buf.getvalue())["reason"], ("checksum_mismatch", "size_mismatch"))


if __name__ == "__main__":
    unittest.main()