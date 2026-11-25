import json
import tempfile
import unittest

from tools.routing_config import load_config, validate_config


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


if __name__ == "__main__":
    unittest.main()