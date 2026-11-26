"""Per-project tool settings: work/config/<tool>.json (pipeline/job-results.md)."""
import json
import sys


def load_config(path, defaults, required=()):
    """defaults overlaid with the JSON file. Unknown keys are an error (typos would
    silently fall back to a default); keys starting with "_" are comments."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        sys.exit(f"config {path}: {exc}")
    data = {k: v for k, v in data.items() if not k.startswith("_")}
    unknown = sorted(set(data) - set(defaults) - set(required))
    missing = sorted(set(required) - set(data))
    if unknown or missing:
        sys.exit(f"config {path}: unknown keys {unknown}, missing keys {missing}")
    return {**defaults, **data}
