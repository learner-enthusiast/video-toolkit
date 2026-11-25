import json
import os
import tempfile
import unittest

# Import from hooks module path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "hooks"))
import projlog  # noqa: E402


class ProjlogUsageTest(unittest.TestCase):
    def test_usage_dedupes_message_id(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            base = {
                "type": "assistant",
                "timestamp": "2026-01-01T12:00:00Z",
                "message": {
                    "id": "msg-1",
                    "usage": {
                        "input_tokens": 10,
                        "cache_creation_input_tokens": 1,
                        "cache_read_input_tokens": 2,
                        "output_tokens": 3,
                    },
                },
            }
            for _ in range(2):
                f.write(json.dumps(base) + "\n")
            path = f.name
        try:
            tot, _, n, models = projlog.usage_since([path], "2026-01-01T11:00:00Z", main_only=True)
            self.assertEqual(n, 1)
            self.assertEqual(tot["input"], 10)
            self.assertIn("unknown", models)
        finally:
            os.remove(path)

    def test_usage_records_model_id(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "type": "assistant",
                        "timestamp": "2026-01-01T12:00:00Z",
                        "message": {
                            "id": "msg-2",
                            "model": "claude-sonnet-5-5",
                            "usage": {
                                "input_tokens": 5,
                                "cache_creation_input_tokens": 0,
                                "cache_read_input_tokens": 0,
                                "output_tokens": 2,
                            },
                        },
                    }
                )
                + "\n"
            )
            path = f.name
        try:
            _, _, n, models = projlog.usage_since([path], "2026-01-01T11:00:00Z", main_only=True)
            self.assertEqual(n, 1)
            self.assertEqual(models["claude-sonnet-5-5"]["input"], 5)
        finally:
            os.remove(path)

    def test_resolve_mentions_longest_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = os.path.join(td, "toolkit")
            os.makedirs(os.path.join(root, "projects", "pl", "01-ep", "raw"))
            with open(os.path.join(root, "CLAUDE.md"), "w") as cf:
                cf.write("rules\n")
            proj, _ = projlog.resolve_mentions(root, "work on projects/pl/01-ep/foo")
            self.assertEqual(proj, "projects/pl/01-ep")


if __name__ == "__main__":
    unittest.main()