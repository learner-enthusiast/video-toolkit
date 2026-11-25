"""Cross-platform safe relative path handling for cache bundles."""
from __future__ import annotations

import json
import os
import re
import stat

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


def lstat_is_symlink(path: str) -> bool:
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(st.st_mode)


def path_has_symlink_component(path: str) -> bool:
    """True if any path component (including the final) is a symlink."""
    path = os.path.normpath(path)
    if not path or path == os.sep:
        return False
    parts = path.split(os.sep)
    if path.startswith(os.sep):
        cur = os.sep
        idx = 1
    else:
        cur = parts[0] or "."
        idx = 1
        if lstat_is_symlink(cur):
            return True
    for i in range(idx, len(parts)):
        cur = os.path.join(cur, parts[i])
        if lstat_is_symlink(cur):
            return True
    return False


def assert_no_symlinks_under(root: str) -> None:
    """Reject symlinked root, parents, or any entry under root (directories included)."""
    root = os.path.normpath(root)
    if not os.path.isdir(root) and not os.path.isfile(root):
        raise ValueError(f"not_a_bundle_root:{root}")
    if path_has_symlink_component(root):
        raise ValueError(f"symlink_forbidden:root")
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        for d in list(dirnames):
            ap = os.path.join(dirpath, d)
            if lstat_is_symlink(ap):
                raise ValueError(f"symlink_forbidden:{os.path.relpath(ap, root)}")
        for fn in filenames:
            ap = os.path.join(dirpath, fn)
            if lstat_is_symlink(ap):
                raise ValueError(f"symlink_forbidden:{os.path.relpath(ap, root)}")


def resolve_contained(root: str, rel: str) -> str | None:
    nrel = normalize_relpath(rel)
    if not nrel:
        return None
    root_abs = os.path.abspath(root)
    joined = os.path.join(root_abs, nrel)
    if path_has_symlink_component(joined):
        return None
    if not os.path.lexists(joined):
        return None
    root_real = os.path.realpath(root_abs)
    candidate = os.path.realpath(joined)
    if candidate == root_real:
        return None
    if not candidate.startswith(root_real + os.sep):
        return None
    return candidate


def safe_project_relpath(project: str, rel: str) -> str | None:
    """Validate a manifest-stored path stays inside the project directory."""
    nrel = normalize_relpath(rel)
    if not nrel:
        return None
    joined = os.path.join(project, nrel)
    if path_has_symlink_component(joined):
        return None
    proj = os.path.realpath(project)
    candidate = os.path.realpath(joined)
    if not candidate.startswith(proj + os.sep) and candidate != proj:
        return None
    return candidate


def resolve_in_asset_bundle(project: str, cache_key: str, rel: str) -> str | None:
    """Output must live under work/cache/bundles/<key>/ (bundle dir not a symlink)."""
    nrel = normalize_relpath(rel)
    if not nrel:
        return None
    exp = normalize_relpath(os.path.join("work", "cache", "bundles", cache_key))
    if not exp:
        return None
    if not (nrel == exp or nrel.startswith(exp + "/")):
        return None
    bundle = os.path.join(project, "work", "cache", "bundles", cache_key)
    if path_has_symlink_component(bundle):
        return None
    joined = os.path.join(project, nrel)
    if path_has_symlink_component(joined):
        return None
    if not os.path.isdir(bundle):
        return None
    bundle_real = os.path.realpath(bundle)
    candidate = os.path.realpath(joined)
    if not candidate.startswith(bundle_real + os.sep):
        return None
    if not os.path.isfile(joined):
        return None
    try:
        st = os.lstat(joined)
    except OSError:
        return None
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        return None
    return candidate


def load_json_dict(path: str) -> tuple[dict | None, str | None]:
    if not os.path.isfile(path):
        return None, "missing"
    try:
        with open(path) as f:
            raw = f.read()
    except OSError:
        return None, "unreadable"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, "corrupt_json"
    if not isinstance(data, dict):
        return None, "invalid_structure"
    return data, None