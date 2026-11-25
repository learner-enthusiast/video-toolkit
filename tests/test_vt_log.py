import json
import os
import tempfile
import unittest

from tools import vt_log


class VtLogTest(unittest.TestCase):
    def test_explicit_stage_line(self):
        body = (
            "### Handoff: 2 · Cut\n"
            "## 2026-01-01\n\n**Prompt:** work/prompts/x.md\n\n"
            "**Finished** 12:00:00 · **Took** 1 s\n"
            "**Stage:** compose\n"
            "**Tokens:** input 10 · cache write 0 · cache read 0 · output 2 "
            "(main session; subagents: input 5 · cache write 0 · cache read 0 · output 1); "
            "models main: claude-sonnet-5-5 in 10 cw 0 cr 0 out 2 | "
            "sub: claude-haiku-5-5 in 5 cw 0 cr 0 out 1\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(body)
            path = f.name
        try:
            summary = vt_log.summarize(vt_log.parse_token_lines(path))
            self.assertEqual(summary["by_stage"]["main"]["compose"]["input"], 10)
            self.assertEqual(summary["by_stage"]["subagents"]["compose"]["input"], 5)
            self.assertEqual(summary["by_model"]["main"]["claude-sonnet-5-5"]["output"], 2)
            self.assertEqual(summary["by_model"]["subagents"]["claude-haiku-5-5"]["output"], 1)
        finally:
            os.remove(path)

    def test_legacy_merged_models(self):
        body = (
            "**Tokens:** input 3 · cache write 0 · cache read 0 · output 1 "
            "(main session; subagents: none); "
            "models: claude-sonnet-5-5 in 3 cw 0 cr 0 out 1\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(body)
            path = f.name
        try:
            summary = vt_log.summarize(vt_log.parse_token_lines(path))
            self.assertEqual(summary["by_model"]["main"]["claude-sonnet-5-5"]["input"], 3)
            self.assertEqual(summary["entries"], 1)
        finally:
            os.remove(path)


    def test_compare_delta(self):
        base = (
            "**Finished** 12:00:00 · **Took** 60 s\n**Stage:** prep\n"
            "**Tokens:** input 100 · cache write 0 · cache read 0 · output 10 (main session; subagents: none)\n"
        )
        cand = (
            "**Finished** 12:01:00 · **Took** 30 s\n**Stage:** prep\n"
            "**Tokens:** input 50 · cache write 0 · cache read 0 · output 5 (main session; subagents: none)\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f1:
            f1.write(base)
            p1 = f1.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f2:
            f2.write(cand)
            p2 = f2.name
        try:
            cmp = vt_log.compare_logs(p1, p2)
            self.assertEqual(cmp["delta_main"]["input"], -50)
            self.assertEqual(cmp["candidate_timing"]["total_seconds"], 30)
        finally:
            os.remove(p1)
            os.remove(p2)


if __name__ == "__main__":
    unittest.main()