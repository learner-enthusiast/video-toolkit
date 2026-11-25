import unittest

from tools import path_safety as ps


class PathSafetyTest(unittest.TestCase):
    def test_rejects_windows_drive(self):
        self.assertIsNone(ps.normalize_relpath("C:/Windows/evil"))

    def test_rejects_unc(self):
        self.assertIsNone(ps.normalize_relpath("//server/share"))

    def test_rejects_absolute_posix(self):
        self.assertIsNone(ps.normalize_relpath("/etc/passwd"))

    def test_rejects_dotdot(self):
        self.assertIsNone(ps.normalize_relpath("foo/../../etc/passwd"))

    def test_containment(self):
        with __import__("tempfile").TemporaryDirectory() as td:
            root = f"{td}/bundle"
            __import__("os").makedirs(root)
            with open(f"{root}/ok.txt", "w") as f:
                f.write("x")
            self.assertIsNotNone(ps.resolve_contained(root, "ok.txt"))
            self.assertIsNone(ps.resolve_contained(root, "../outside.txt"))


if __name__ == "__main__":
    unittest.main()