"""Load and validate config/model-routing.json (single source of model IDs)."""
from __future__ import annotations

import json
import os
from typing import Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "model-routing.json")
REQUIRED_TIERS = ("production", "creative", "worker")
OPTIONAL_TIERS = ("escalation",)
VALID_EFFORT = frozenset({"low", "medium", "high"})
CHECKPOINT_TASKS = frozenset(
    {"creative_direction", "approval_stills_review", "final_visual_qa"}
)


def load_config(path: str | None = None) -> dict:
    path = path or CONFIG_PATH
    with open(path) as f:
        return json.load(f)


def tier_names(config: dict, tier: str) -> set[str]:
    """Every string that selects a tier: its id and aliases."""
    block = (config.get("models") or {}).get(tier) or {}
    return {n for n in [block.get("id"), *block.get("aliases", [])] if n}


def agent_frontmatter(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        parts = f.read().split("---\n", 2)
    if len(parts) < 3 or parts[0]:
        return {}
    pairs = (line.split(":", 1) for line in parts[1].splitlines() if ":" in line)
    return {key.strip(): value.strip() for key, value in pairs}


def validate_claude_files(config: dict, root: str) -> list[dict]:
    """.claude/agents/*.md and settings.json must use the tier the config assigns them."""
    errs: list[dict] = []

    def err(code, message, field):
        errs.append({"code": code, "message": message, "field": field})

    wanted = {
        spec["agent"]: spec.get("model")
        for spec in (config.get("subagents") or {}).values() if spec.get("agent")
    }
    agents_dir = os.path.join(root, ".claude", "agents")
    present = (
        {f[:-3] for f in os.listdir(agents_dir) if f.endswith(".md")}
        if os.path.isdir(agents_dir) else set()
    )
    for name in sorted(present - set(wanted)):
        err("AGENT_UNROUTED", f"{name}.md has no subagents entry in the routing config", name)
    for name, tier in sorted(wanted.items()):
        if name not in present:
            err("AGENT_MISSING", f".claude/agents/{name}.md not found", name)
            continue
        meta = agent_frontmatter(os.path.join(agents_dir, f"{name}.md"))
        if meta.get("name") != name:
            err("AGENT_NAME", f"{name}.md frontmatter name is {meta.get('name')!r}", name)
        if meta.get("model") not in tier_names(config, tier):
            err("AGENT_MODEL", f"{name} model {meta.get('model')!r} is not the {tier} tier", name)
        if not meta.get("tools"):
            err("AGENT_TOOLS", f"{name} must list its tools", name)

    runner = (config.get("subagents") or {}).get("heavy_job_runner") or {}
    if runner:
        if runner.get("type") != "script" or "model" in runner:
            err("RUNNER_NOT_SCRIPT", "heavy_job_runner must be a script, not a model", "heavy_job_runner")
        elif not os.path.isfile(os.path.join(root, runner.get("script") or "")):
            err("RUNNER_MISSING", f"runner script {runner.get('script')!r} not found", "heavy_job_runner")

    session = config.get("session_default")
    if session:
        try:
            with open(os.path.join(root, session["settings_file"]), encoding="utf-8") as f:
                model = json.load(f).get("model")
        except (OSError, ValueError, KeyError):
            err("SETTINGS_UNREADABLE", "cannot read the session settings file", "session_default")
        else:
            if model not in tier_names(config, session.get("model")):
                err("SETTINGS_MODEL",
                    f"settings model {model!r} is not the {session.get('model')} tier", "session_default")
    return errs


def tier_id(config: dict, tier: str) -> str | None:
    block = (config.get("models") or {}).get(tier) or {}
    return block.get("id")


def validate_config(config: dict) -> list[dict]:
    """Return list of errors {code, message, field?}."""
    errs: list[dict] = []
    if config.get("schema_version") != 1:
        errs.append({"code": "SCHEMA_VERSION", "message": "schema_version must be 1"})
    models = config.get("models")
    if not isinstance(models, dict):
        errs.append({"code": "MODELS_MISSING", "message": "models object required"})
        return errs
    for tier in REQUIRED_TIERS:
        if tier not in models:
            errs.append({"code": "MISSING_TIER", "message": f"Missing tier {tier}", "field": tier})
        else:
            mid = models[tier].get("id")
            if not mid or not isinstance(mid, str):
                errs.append({"code": "MISSING_ID", "message": f"{tier} needs id", "field": tier})
            eff = models[tier].get("default_effort")
            if eff and eff not in VALID_EFFORT:
                errs.append({"code": "BAD_EFFORT", "message": f"{tier} effort {eff!r}", "field": tier})
    ids = [models[t].get("id") for t in models if isinstance(models.get(t), dict)]
    ids = [i for i in ids if i]
    if len(ids) != len(set(ids)):
        errs.append({"code": "DUPLICATE_ID", "message": "Duplicate model ids across tiers"})
    subs = config.get("subagents") or {}
    vqa = subs.get("vision_qa") or {}
    if vqa.get("same_as_main") is True:
        errs.append({"code": "VISION_SAME_AS_MAIN", "message": "vision_qa must not use same_as_main"})
    if vqa.get("model") != "creative":
        errs.append({"code": "VISION_TIER", "message": "vision_qa.model must be creative"})
    for name, cp in (config.get("checkpoints") or {}).items():
        if cp.get("model") == "creative" and cp.get("task") not in CHECKPOINT_TASKS:
            errs.append({"code": "CHECKPOINT_TASK", "message": f"Unknown checkpoint task for {name}"})
    effort = config.get("effort_levels") or {}
    for task, spec in (effort.get("default_by_task_class") or {}).items():
        if spec.get("effort") not in VALID_EFFORT:
            errs.append({"code": "BAD_TASK_EFFORT", "message": f"task {task} effort invalid"})
        tier = spec.get("model")
        if tier and tier not in models:
            errs.append({"code": "BAD_TASK_MODEL", "message": f"task {task} references unknown tier {tier}"})
    return errs