"""Cross-platform safe relative path handling for cache bundles."""
from __future__ import annotations

import os
import re

_WIN_DRIVE = re.compile(r"^[A-Za-z]:")


def normalize_relpath(rel: str) -> str | None:
    if not rel or not isinstance(rel, str) or "\x00" in rel:
        return None
    s = rel.strip().replace("\\", "/")
    if _WIN_DRIVE.match(s) or s.startswith("//") or s.startswith("\\\\"):
        return None
    if s.startswith("/"):
        return None
    norm = os.path.normpath(s).replace("\\", "/")
    if norm in (".", ""):
        return None
    parts = norm.split("/")
    if any(p == ".." for p in parts):
        return None
    if norm.startswith("../"):
        return None
    return norm


def resolve_contained(root: str, rel: str) -> str | None:
    nrel = normalize_relpath(rel)
    if not nrel:
        return None
    root_real = os.path.realpath(root)
    candidate = os.path.realpath(os.path.join(root, nrel))
    if candidate == root_real:
        return None
    if not (candidate.startswith(root_real + os.sep)):
        return None
    return candidate


def safe_project_relpath(project: str, rel: str) -> str | None:
    """Validate a manifest-stored path stays inside the project directory."""
    nrel = normalize_relpath(rel)
    if not nrel:
        return None
    proj = os.path.realpath(project)
    candidate = os.path.realpath(os.path.join(project, nrel))
    if not candidate.startswith(proj + os.sep) and candidate != proj:
        return None
    return candidate