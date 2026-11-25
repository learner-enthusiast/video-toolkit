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

    def test_symlink_output_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            inp = os.path.join(proj, "in.bin")
            real = os.path.join(proj, "real.bin")
            with open(inp, "wb") as f:
                f.write(b"data")
            with open(real, "wb") as f:
                f.write(b"result")
            key = ac.cache_key("probe", inp, None, tool_version="1.0")
            bundle = ac.bundle_root(proj, key)
            os.makedirs(bundle)
            os.symlink(real, os.path.join(bundle, "out.bin"))
            rel = os.path.relpath(os.path.join(bundle, "out.bin"), proj).replace("\\", "/")
            ent = {
                "op": "probe",
                "path": rel,
                "input": os.path.abspath(inp),
                "params": None,
                "tool_version": "1.0",
                "schema": ac.CACHE_VERSION,
                "cache_key": key,
                "size": 6,
                "sha256": ac.sha256_file(real),
                "implementation": ac.implementation_hash(),
            }
            ok, reason = ac.verify_entry(proj, ent, key)
            self.assertFalse(ok)
            self.assertEqual(reason, "path_forbidden")

    def test_path_outside_key_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            inp = os.path.join(proj, "in.bin")
            other = os.path.join(proj, "work", "cache", "bundles", "otherkey", "out.bin")
            os.makedirs(os.path.dirname(other), exist_ok=True)
            with open(inp, "wb") as f:
                f.write(b"data")
            with open(other, "wb") as f:
                f.write(b"result")
            key = ac.cache_key("probe", inp, None, tool_version="1.0")
            rel = os.path.relpath(other, proj).replace("\\", "/")
            ent = {
                "op": "probe",
                "path": rel,
                "input": os.path.abspath(inp),
                "params": None,
                "tool_version": "1.0",
                "schema": ac.CACHE_VERSION,
                "cache_key": key,
                "size": 6,
                "sha256": ac.sha256_file(other),
                "implementation": ac.implementation_hash(),
            }
            ok, reason = ac.verify_entry(proj, ent, key)
            self.assertFalse(ok)
            self.assertEqual(reason, "path_forbidden")

    def test_corrupt_manifest_quarantined_on_write(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            mp = ac.manifest_path(proj)
            os.makedirs(os.path.dirname(mp))
            with open(mp, "w") as f:
                f.write("{broken json")
            inp = os.path.join(proj, "in.bin")
            out = os.path.join(proj, "out.bin")
            with open(inp, "wb") as f:
                f.write(b"x")
            with open(out, "wb") as f:
                f.write(b"y")
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
                    "tool_version": "1.0",
                },
            )()
            ac.cmd_store(store)
            self.assertTrue(os.path.isfile(mp + ".corrupt"))


if __name__ == "__main__":
    unittest.main()