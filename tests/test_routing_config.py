import json
import os
import shutil
import tempfile
import unittest

from tools.routing_config import load_config, validate_claude_files, validate_config

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class RoutingConfigTest(unittest.TestCase):
    def test_valid_config(self):
        cfg = load_config()
        errs = validate_config(cfg)
        self.assertEqual(errs, [])

    def test_reject_same_as_main(self):
        cfg = load_config()
        cfg["subagents"]["vision_qa"]["same_as_main"] = True
        errs = validate_config(cfg)
        self.assertTrue(any(e["code"] == "VISION_SAME_AS_MAIN" for e in errs))

    def test_agents_and_settings_match_their_tiers(self):
        self.assertEqual(validate_claude_files(load_config(), REPO), [])

    def claude_errors(self, mutate):
        with tempfile.TemporaryDirectory() as td:
            shutil.copytree(os.path.join(REPO, ".claude", "agents"), os.path.join(td, ".claude", "agents"))
            shutil.copy(os.path.join(REPO, ".claude", "settings.json"), os.path.join(td, ".claude"))
            mutate(os.path.join(td, ".claude"))
            return {e["code"] for e in validate_claude_files(load_config(), td)}

    @staticmethod
    def rewrite(path, old, new):
        with open(path) as f:
            text = f.read()
        assert old in text
        with open(path, "w") as f:
            f.write(text.replace(old, new))

    def test_wrong_agent_model_is_rejected(self):
        codes = self.claude_errors(lambda d: self.rewrite(
            os.path.join(d, "agents", "vision-qa.md"), "model: claude-opus-5-5", "model: haiku"))
        self.assertEqual(codes, {"AGENT_MODEL"})

    def test_missing_and_unrouted_agents_are_rejected(self):
        codes = self.claude_errors(lambda d: os.rename(
            os.path.join(d, "agents", "vision-qa.md"), os.path.join(d, "agents", "other.md")))
        self.assertEqual(codes, {"AGENT_MISSING", "AGENT_UNROUTED"})

    def test_wrong_session_model_is_rejected(self):
        codes = self.claude_errors(lambda d: self.rewrite(
            os.path.join(d, "settings.json"), "claude-sonnet-5-5", "claude-opus-5-5"))
        self.assertEqual(codes, {"SETTINGS_MODEL"})


if __name__ == "__main__":
    unittest.main()