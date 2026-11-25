import json
import os
import tempfile
import unittest

from tools.scaffold_remotion import remotion_version, scaffold


class ScaffoldTest(unittest.TestCase):
    def test_scaffold_structure(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            path = scaffold(proj, "9:16")
            self.assertTrue(os.path.isfile(os.path.join(path, "package.json")))
            self.assertTrue(os.path.isfile(os.path.join(path, "src", "lib", "layout.ts")))
            self.assertTrue(os.path.isfile(os.path.join(path, "src", "Root.tsx")))
            self.assertTrue(os.path.islink(os.path.join(path, "src", "shared")))
            with open(os.path.join(path, "package.json")) as pf:
                pkg = json.load(pf)
            self.assertEqual(pkg["dependencies"]["remotion"], remotion_version())

    def test_refuse_non_empty(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            rem = os.path.join(proj, "work", "remotion")
            os.makedirs(rem)
            with open(os.path.join(rem, "keep.txt"), "w") as kf:
                kf.write("x")
            with self.assertRaises(SystemExit):
                scaffold(proj, "9:16")


if __name__ == "__main__":
    unittest.main()