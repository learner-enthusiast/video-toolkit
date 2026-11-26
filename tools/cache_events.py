"""Cache hit/miss events, kept beside each project's cache manifests (read by `vt_log.py record`)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

EVENTS = "work/cache/events.jsonl"


def record(project: str, cache: str, op: str, result: str, reason: str) -> None:
    """result: hit | miss | bypass (final QA, which is never cached). Never raises."""
    try:
        path = os.path.join(project, EVENTS)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        row = {"ts": datetime.now(timezone.utc).isoformat(), "cache": cache, "op": op,
               "result": result, "reason": reason}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def read(project: str) -> list[dict] | None:
    """All events, or None when nothing was ever recorded (unknown, not zero)."""
    try:
        with open(os.path.join(project, EVENTS), encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows
