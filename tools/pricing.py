"""Cost-weighted token totals from config/model-routing.json. A comparison metric, not a bill."""
from __future__ import annotations

import re

from tools import routing_config

WEIGHT_KEYS = ("input", "cache_write", "cache_read", "output")


def tier_for(model: str, config: dict) -> str | None:
    """The routing tier of a transcript model string (id, long-context id, alias or dated id)."""
    base = re.sub(r"\[[^\]]*\]$", "", model or "")
    base = re.sub(r"-20\d{6}$", "", base)
    for tier, block in (config.get("models") or {}).items():
        names = routing_config.tier_names(config, tier)
        if block.get("long_context_id"):
            names.add(block["long_context_id"])
        if model in names or base in {re.sub(r"\[[^\]]*\]$", "", n) for n in names}:
            return tier
    return None


def weighted_cost(models: dict[str, dict], config: dict) -> tuple[float | None, list[str]]:
    """(USD-equivalent, unpriced models). None when any model with usage has no price."""
    weights = (config.get("cost") or {}).get("weights") or {}
    total, unpriced = 0.0, []
    for model, usage in sorted(models.items()):
        if not any(usage.get(k) for k in WEIGHT_KEYS):
            continue
        tier = tier_for(model, config)
        price = ((config.get("models") or {}).get(tier) or {}).get("input_price_usd_per_mtok")
        if price is None or set(WEIGHT_KEYS) - set(weights):
            unpriced.append(model)
            continue
        total += price * sum(usage.get(k, 0) * weights[k] for k in WEIGHT_KEYS) / 1_000_000
    return (None if unpriced else total), unpriced
