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