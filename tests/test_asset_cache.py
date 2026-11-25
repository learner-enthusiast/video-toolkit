import os
import tempfile
import unittest

from tools import asset_cache as ac


class AssetCacheTest(unittest.TestCase):
    def test_store_and_lookup(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            inp = os.path.join(proj, "in.bin")
            out = os.path.join(proj, "out.bin")
            open(inp, "wb").write(b"data")
            open(out, "wb").write(b"result")
            args = type("A", (), {"project": proj, "input": inp, "op": "probe", "params": "", "output": out})()
            ac.cmd_store(args)
            lookup = type("A", (), {"project": proj, "input": inp, "op": "probe", "params": ""})()
            try:
                ac.cmd_lookup(lookup)
            except SystemExit as e:
                self.assertEqual(e.code, 0, "expected cache hit")


if __name__ == "__main__":
    unittest.main()