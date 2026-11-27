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

    def test_brand_is_written_to_env(self):
        for brand in (1, 2, 3):
            with self.subTest(brand=brand), tempfile.TemporaryDirectory() as td:
                path = scaffold(td, "9:16", brand=brand)
                with open(os.path.join(path, ".env")) as env:
                    self.assertEqual(env.read(), f"REMOTION_BRAND={brand}\n")

    def test_default_brand_is_1(self):
        with tempfile.TemporaryDirectory() as td:
            path = scaffold(td, "9:16")
            with open(os.path.join(path, ".env")) as env:
                self.assertEqual(env.read(), "REMOTION_BRAND=1\n")

    def test_unknown_brand_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            for brand in (0, 4, "2"):
                with self.subTest(brand=brand), self.assertRaises(SystemExit):
                    scaffold(td, "9:16", brand=brand)
            self.assertFalse(os.path.exists(os.path.join(td, "work")))

    def test_remotion_packages_share_one_version(self):
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(scaffold(td, "9:16"), "package.json")) as pf:
                deps = json.load(pf)["dependencies"]
            self.assertEqual({v for k, v in deps.items() if k == "remotion" or k.startswith("@remotion/")}, {remotion_version()})


if __name__ == "__main__":
    unittest.main()