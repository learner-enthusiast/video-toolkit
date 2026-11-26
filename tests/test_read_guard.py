import json
import os
import subprocess
import sys
import tempfile
import unittest

from tools.hooks.read_guard import blocked_reason

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOK = os.path.join(REPO, "tools", "hooks", "read_guard.py")


class ReadGuardTest(unittest.TestCase):
    def test_blocked_paths(self):
        for path in (
            "icons/icons.md", "components/index-full.md",
            "projects/demo/raw/take.txt", "projects/pl/01-ep/raw/a/b.jpg",
            "projects/demo/work/remotion/node_modules/remotion/index.d.ts", "node_modules/x.js",
            "projects/demo/out/final.MP4", "a/b.mov", "projects/demo/work/audio/clean.wav",
            os.path.join(REPO, "icons", "icons.md"),
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(blocked_reason(path, REPO))

    def test_allowed_paths(self):
        for path in (
            "components/index.md", "components/specs/Counter.md", "brand.md",
            "projects/demo/work/storyboard.md", "projects/demo/work/inspect/contact_sheet.jpg",
            "projects/demo/assets/shot.png", "/etc/hostname",
        ):
            with self.subTest(path=path):
                self.assertIsNone(blocked_reason(path, REPO))

    def test_small_ranged_read_of_lookup_tables_allows_edits(self):
        self.assertIsNone(blocked_reason("icons/icons.md", REPO, limit=40))
        self.assertIsNone(blocked_reason("components/index-full.md", REPO, limit=1))
        for limit in (41, 2000, 0, None, "10"):
            self.assertIsNotNone(blocked_reason("icons/icons.md", REPO, limit=limit))
        # A range never unlocks media or raw footage.
        self.assertIsNotNone(blocked_reason("projects/demo/raw/notes.md", REPO, limit=1))

    def test_symlink_to_a_blocked_file(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "icons"))
            os.makedirs(os.path.join(td, "public"))
            open(os.path.join(td, "icons", "icons.md"), "w").close()
            os.symlink("../icons", os.path.join(td, "public", "icons"))
            self.assertIsNotNone(blocked_reason("public/icons/icons.md", td))

    def run_hook(self, payload):
        return subprocess.run(
            [sys.executable, HOOK], input=payload, capture_output=True, text=True, timeout=20,
            env={**os.environ, "CLAUDE_PROJECT_DIR": REPO},
        )

    def test_hook_exit_codes(self):
        def call(tool, path):
            return self.run_hook(json.dumps({"tool_name": tool, "tool_input": {"file_path": path}}))

        blocked = call("Read", "icons/icons.md")
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("grep -i", blocked.stderr)
        self.assertEqual(call("Read", "brand.md").returncode, 0)
        self.assertEqual(call("Edit", "icons/icons.md").returncode, 0)
        self.assertEqual(self.run_hook("not json").returncode, 0)  # fails open


class SettingsTest(unittest.TestCase):
    def test_shell_lookups_are_not_denied(self):
        """A Read deny rule also blocks Bash commands naming the file, so only the
        Read-only hook may cover files that the toolkit greps, probes or copies."""
        with open(os.path.join(REPO, ".claude", "settings.json")) as f:
            settings = json.load(f)
        denied = " ".join(settings["permissions"]["deny"])
        for needle in ("icons.md", "index-full", "raw", "node_modules", ".mp4", ".mov", ".wav"):
            self.assertNotIn(needle, denied)
        self.assertIn("Bash(grep:*)", settings["permissions"]["allow"])
        hooks = settings["hooks"]
        self.assertEqual(hooks["PreToolUse"][0]["matcher"], "Read")
        self.assertIn("read_guard.py", hooks["PreToolUse"][0]["hooks"][0]["command"])
        self.assertIn("session_brief.py", hooks["SessionStart"][0]["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
