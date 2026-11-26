"""Footer call counts and cost, vt_log parsing and the per-stage record."""
import json
import os
import sys
import tempfile
import unittest

from tests.tool_fixtures import REPO, read_json, run, tool, write, write_json
from tools import cache_events, pricing, routing_config, vt_log
from tools.hooks import projlog, transcript_ckpt as tck

SONNET, OPUS = "claude-sonnet-5-5", "claude-opus-5-5"


def usage(i=0, cw=0, cr=0, o=0):
    return {"input": i, "cache_write": cw, "cache_read": cr, "output": o}


def entry(stage, hhmm, cost="0.5000", calls=True, took="1 m 00 s"):
    lines = [
        f"## 2026-01-05 {hhmm} IST · turn", "", "**Prompt:** work/prompts/x.md", "",
        f"**Finished** {hhmm}:59 · **Took** {took}", f"**Stage:** {stage}",
        "**Tokens:** input 10 · cache write 20 · cache read 30 · output 40 (main session; subagents: input 1 · "
        f"cache write 2 · cache read 3 · output 4); models main: {SONNET} in 10 cw 20 cr 30 out 40 | "
        f"sub: {OPUS} in 1 cw 2 cr 3 out 4",
    ]
    if calls:
        lines.append(f"**Calls:** main 5 · sidechain 0 · subagents 2; by model: {OPUS} 2 · {SONNET} 5")
    if cost:
        lines.append(f"**Cost:** weighted USD {cost}")
    return "\n".join(lines) + "\n\n**Changes:** something\n\n"


class PricingTest(unittest.TestCase):
    def test_weights_and_prices_come_from_config(self):
        cfg = routing_config.load_config()
        cfg["models"]["production"]["input_price_usd_per_mtok"] = 2
        total, unpriced = pricing.weighted_cost({SONNET: usage(1_000_000, 1_000_000, 1_000_000, 1_000_000)}, cfg)
        self.assertAlmostEqual(total, 2 * (1 + 1.25 + 0.1 + 5))
        self.assertEqual(unpriced, [])
        cfg["cost"]["weights"]["output"] = 1
        self.assertAlmostEqual(pricing.weighted_cost({SONNET: usage(o=1_000_000)}, cfg)[0], 2)

    def test_unknown_model_is_not_priced_as_zero(self):
        cfg = routing_config.load_config()
        self.assertEqual(pricing.weighted_cost({"mystery-1": usage(5)}, cfg), (None, ["mystery-1"]))
        self.assertEqual(pricing.weighted_cost({"<synthetic>": usage()}, cfg), (0.0, []))
        self.assertEqual(pricing.tier_for("claude-sonnet-5-5[1m]", cfg), "production")

    def test_config_without_prices_is_rejected(self):
        cfg = routing_config.load_config()
        del cfg["models"]["creative"]["input_price_usd_per_mtok"]
        cfg["cost"]["weights"].pop("cache_read")
        self.assertEqual({e["code"] for e in routing_config.validate_config(cfg)}, {"MISSING_PRICE", "BAD_COST_WEIGHT"})


class FooterTest(unittest.TestCase):
    def test_footer_lines_round_trip_through_vt_log(self):
        models = {SONNET: usage(1000, 0, 0, 100)}
        footer = "\n".join([
            "**Tokens:** " + projlog.fmt(usage(1000, o=100)) + " (main session; subagents: none)"
            + projlog.fmt_models_footer(models, {}),
            projlog.fmt_calls_footer(3, 1, 2, {SONNET: 4, OPUS: 2}),
            projlog.fmt_cost_footer(models, {}),
        ])
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "log.md")
            write(path, footer + "\n\n## later\n")
            (e,) = vt_log.parse_token_lines(path)
        self.assertEqual(e["calls"], {"main": 3, "sidechain": 1, "subagents": 2, "by_model": {SONNET: 4, OPUS: 2}})
        self.assertAlmostEqual(e["cost_weighted_usd"], 2 * (1000 + 500) / 1e6, places=4)
        self.assertEqual(list(e["models_main"]), [SONNET])

    def test_stop_hook_writes_calls_and_cost(self):
        with tempfile.TemporaryDirectory() as td:
            write(os.path.join(td, "CLAUDE.md"), "rules\n")
            os.makedirs(os.path.join(td, "projects", "demo", "raw"))
            projlog.cmd_prompt({"session_id": "s", "prompt": "work on projects/demo"}, td)
            transcript = os.path.join(td, "t.jsonl")
            rows = [{"type": "assistant", "timestamp": "2999-01-01T00:00:0%dZ" % i, "isSidechain": i == 2,
                     "message": {"id": f"m{i}", "model": SONNET, "usage": {"input_tokens": 10, "output_tokens": 1}}}
                    for i in range(3)]
            write(transcript, "".join(json.dumps(r) + "\n" for r in rows + rows[:1]))
            os.environ["PROJLOG_NO_WAIT"] = "1"
            try:
                projlog.cmd_tokens({"session_id": "s", "transcript_path": transcript}, td)
            finally:
                del os.environ["PROJLOG_NO_WAIT"]
            with open(os.path.join(td, "projects", "demo", "log.md")) as f:
                log = f.read()
        self.assertIn(f"**Calls:** main 2 · sidechain 1 · subagents 0; by model: {SONNET} 3", log)
        self.assertRegex(log, r"\*\*Cost:\*\* weighted USD \d+\.\d{4}")


class SummaryTest(unittest.TestCase):
    def write_log(self, td, *entries, name="log.md"):
        path = os.path.join(td, name)
        write(path, "# Log\n\n" + "".join(entries))
        return path

    def test_every_entry_keeps_its_own_models(self):
        with tempfile.TemporaryDirectory() as td:
            parsed = vt_log.parse_token_lines(self.write_log(td, entry("cut", "10:00"), entry("cut", "10:10")))
        self.assertEqual([list(e["models_main"]) for e in parsed], [[SONNET], [SONNET]])
        self.assertEqual([list(e["models_subagents"]) for e in parsed], [[OPUS], [OPUS]])

    def test_totals_are_null_when_any_entry_lacks_the_measure(self):
        with tempfile.TemporaryDirectory() as td:
            full = self.write_log(td, entry("cut", "10:00"), entry("cut", "10:10", cost="0.2500"), name="a.md")
            old = self.write_log(td, entry("cut", "10:00"), entry("cut", "10:10", cost=None, calls=False), name="b.md")
            summary = vt_log.summarize(vt_log.parse_token_lines(full))
            partial = vt_log.summarize(vt_log.parse_token_lines(old))
            compare = vt_log.compare_logs(full, full)
            mixed = vt_log.compare_logs(old, full)
        self.assertEqual(summary["cost_weighted_usd"], 0.75)
        self.assertEqual(summary["calls"]["main"], 10)
        self.assertEqual((partial["calls"], partial["cost_weighted_usd"], partial["entries_without_calls_or_cost"]), (None, None, 1))
        self.assertEqual(compare["delta_cost_weighted_usd"], 0)
        self.assertEqual((mixed["delta_calls"], mixed["delta_cost_weighted_usd"]), (None, None))


class RecordTest(unittest.TestCase):
    def record(self, proj, *args):
        r = run([sys.executable, tool("vt_log.py"), "record", proj, *args], cwd=REPO)
        return read_json(r.stdout.strip()), r

    def test_full_record(self):
        with tempfile.TemporaryDirectory() as proj:
            write(os.path.join(proj, "log.md"),
                  entry("compose", "09:00") + entry("cut", "10:00") + entry("cut", "10:10", took="30 s")
                  + "**Approval:** rough_cut=approved\n")
            cache_events.record(proj, "asset", "whisper", "hit", "hit")
            cache_events.record(proj, "asset", "ffprobe", "miss", "miss")
            cache_events.record(proj, "inspect", "thorough", "bypass", "final_qa_requires_fresh_run")
            d = os.path.join(proj, "work", "delegation")
            write(os.path.join(d, "01-copilot-boilerplate.log"), "did it\nEXIT 0\n")
            write_json(os.path.join(d, "01-copilot-boilerplate.usage.json"), {"premiumRequests": 1})
            rec, _ = self.record(proj, "--stage", "cut", "--validators", "pass")
            self.assertEqual(len(os.listdir(os.path.join(proj, "work", "metrics"))), 1)
        self.assertEqual(rec["turns"], 2)
        self.assertEqual(rec["model_calls"]["by_tier"], {"creative": 4, "production": 10})
        self.assertEqual(rec["tokens"]["main"], usage(20, 40, 60, 80))
        self.assertEqual(rec["tokens"]["subagents"], usage(2, 4, 6, 8))
        self.assertEqual(rec["cost_weighted_usd"], 1.0)
        self.assertEqual(rec["wall_time"], {"turn_seconds": 90, "span_seconds": 630})
        self.assertEqual(rec["cache"]["asset"], {"hits": 1, "misses": 1})
        self.assertEqual(rec["cache"]["inspect"], {"hits": 0, "misses": 0, "final_qa_bypasses": 1})
        self.assertEqual(rec["delegation"], [{"log": "01-copilot-boilerplate.log", "tool": "copilot",
                                              "exit_code": 0, "usage": {"premiumRequests": 1}}])
        self.assertEqual(rec["quality"], {"validators_passed": True, "fresh_final_qa_passed": None, "user_approval": True})

    def test_missing_values_are_null(self):
        with tempfile.TemporaryDirectory() as proj:
            write(os.path.join(proj, "log.md"), entry("cut", "10:00", cost=None, calls=False))
            old, _ = self.record(proj, "--stage", "cut")
            none, r = self.record(proj, "--stage", "deliver")
        self.assertIsNone(old["model_calls"])
        self.assertIsNone(old["cost_weighted_usd"])
        self.assertIsNotNone(old["tokens"])
        self.assertEqual(old["cache"], {"asset": None, "inspect": None})
        self.assertIsNone(old["delegation"])
        self.assertEqual(set(old["quality"].values()), {None})
        self.assertIn("no log.md turns", r.stderr)
        for key in ("model_calls", "tokens", "cost_weighted_usd", "window_start", "delegation"):
            self.assertIsNone(none[key], key)

    def test_since_selects_one_run(self):
        with tempfile.TemporaryDirectory() as proj:
            write(os.path.join(proj, "log.md"), entry("cut", "10:00") + entry("cut", "11:00"))
            rec, _ = self.record(proj, "--stage", "cut", "--since", "2026-01-05 10:30")
        self.assertEqual(rec["turns"], 1)

    def test_the_stop_hook_does_not_record(self):
        for name in ("projlog.py", "log_tokens.sh"):
            with open(os.path.join(REPO, "tools", "hooks", name)) as f:
                self.assertNotIn("stage_record", f.read())


class LoggedIdOrderTest(unittest.TestCase):
    def test_the_cap_drops_the_oldest_ids_not_the_alphabetically_first(self):
        old_cap, tck._GLOBAL_ID_CAP = tck._GLOBAL_ID_CAP, 3
        try:
            ckpt = {}
            tck.merge_global_logged_ids(ckpt, ["z-oldest", "y-older"])
            tck.merge_global_logged_ids(ckpt, ["b-new", "a-newest", "z-oldest"])
        finally:
            tck._GLOBAL_ID_CAP = old_cap
        self.assertEqual(ckpt["logged_ids_global"], ["y-older", "b-new", "a-newest"])

    def test_scan_keeps_transcript_order_and_trims_the_oldest_per_file(self):
        old_cap, tck._FILE_ID_CAP = tck._FILE_ID_CAP, 2
        try:
            with tempfile.TemporaryDirectory() as td:
                path = os.path.join(td, "t.jsonl")
                write(path, "".join(json.dumps(
                    {"type": "assistant", "timestamp": "2026-01-01T00:00:00Z",
                     "message": {"id": i, "model": SONNET, "usage": {"input_tokens": 1}}}) + "\n"
                    for i in ("m-z", "m-a", "m-b")))
                ckpt = {"files": {}, "logged_ids_global": []}
                tck.scan_parent_transcript(path, "2025-01-01", set(), checkpoint=ckpt, session_id="s")
        finally:
            tck._FILE_ID_CAP = old_cap
        self.assertEqual(ckpt["logged_ids_global"], ["m-z", "m-a", "m-b"])
        self.assertEqual(ckpt["files"][path]["logged_ids"], ["m-a", "m-b"])


if __name__ == "__main__":
    unittest.main()
