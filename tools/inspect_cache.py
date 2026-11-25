#!/usr/bin/env python3
"""Content-addressed cache for full video-inspect output directories."""
from __future__ import annotations

import argparse
import fcntl
import fnmatch
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

from tools import path_safety as ps

CACHE_SCHEMA = 3
MANIFEST = "work/inspect/.cache-manifest.json"
REQUIRED_FOR_FULL = ("report.json",)
REQUIRED_FOR_VISUAL = ("report.json", "contact_sheet.jpg")
METADATA_FILES = frozenset({"bundle.json", "integrity.json"})


def sha256_file(path: str, chunk=1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def implementation_hash() -> str:
    return sha256_file(os.path.abspath(__file__))[:16]


def probe_meta(path: str) -> dict:
    size = os.path.getsize(path) if os.path.isfile(path) else 0
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=size,duration",
                "-of",
                "json",
                path,
            ],
            text=True,
            timeout=30,
        )
        fmt = json.loads(out).get("format") or {}
        return {
            "size": int(fmt.get("size") or size),
            "duration": float(fmt.get("duration") or 0),
            "probe": "ok",
        }
    except FileNotFoundError:
        return {"size": size, "duration": None, "probe": "unavailable"}
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, subprocess.TimeoutExpired, OSError):
        return {"size": size, "duration": None, "probe": "failed"}


def hash_paths(paths: list[str]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        if os.path.isfile(p):
            h.update(p.encode())
            h.update(sha256_file(p).encode())
    return h.hexdigest()[:16]


def fingerprint(video: str, args) -> str:
    meta = probe_meta(video)
    parts = [
        f"schema{CACHE_SCHEMA}",
        implementation_hash(),
        sha256_file(video),
        str(meta["size"]),
        f"{meta['duration']:.3f}" if meta.get("duration") is not None else "na",
        meta.get("probe", "unknown"),
        args.mode,
        str(args.start if args.start is not None else 0),
        str(args.end if args.end is not None else "end"),
    ]
    if args.inspect_script:
        parts.append(hash_paths([args.inspect_script]))
    if args.ocr_script:
        parts.append(hash_paths([args.ocr_script]))
    if args.config_hash:
        parts.append(args.config_hash)
    if getattr(args, "model_id", None):
        parts.append(str(args.model_id))
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def manifest_path(project: str) -> str:
    return os.path.join(project, MANIFEST)


def _manifest_read_error(data) -> str | None:
    if data.get("schema") != CACHE_SCHEMA:
        return "schema_mismatch"
    entries = data.get("entries")
    if entries is None:
        return None
    if not isinstance(entries, dict):
        return "invalid_entries"
    return None


def _read_manifest_file(project: str) -> dict:
    p = manifest_path(project)
    if not os.path.isfile(p):
        return {"schema": CACHE_SCHEMA, "entries": {}}
    try:
        with open(p) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return {"schema": CACHE_SCHEMA, "entries": {}, "_corrupt_previous": True}
    if not isinstance(data, dict):
        return {"schema": CACHE_SCHEMA, "entries": {}, "_manifest_error": "invalid_manifest"}
    err = _manifest_read_error(data)
    if err:
        return {"schema": CACHE_SCHEMA, "entries": {}, "_manifest_error": err}
    data.setdefault("entries", {})
    return data


def _quarantine_manifest(project: str) -> str | None:
    p = manifest_path(project)
    if not os.path.isfile(p):
        return None
    base = p + ".corrupt"
    target = base
    n = 0
    while os.path.isfile(target):
        n += 1
        target = f"{base}-{n}"
    try:
        shutil.copy2(p, target)
        return target
    except OSError:
        return None


def manifest_transaction(project: str, mutate) -> dict:
    """Lock → read → mutate → atomic write."""
    p = manifest_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lock_path = p + ".lock"
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".manifest-")
    with open(lock_path, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            man = _read_manifest_file(project)
            read_err = None
            if man.get("_corrupt_previous"):
                read_err = "corrupt_json"
            elif man.get("_manifest_error"):
                read_err = man["_manifest_error"]
            if read_err and os.path.isfile(p):
                if _quarantine_manifest(project) is None:
                    raise RuntimeError(f"inspect manifest quarantine failed: {read_err}")
                man = {"schema": CACHE_SCHEMA, "entries": {}}
            man.pop("_corrupt_previous", None)
            man.pop("_manifest_error", None)
            mutate(man)
            man["schema"] = CACHE_SCHEMA
            with os.fdopen(fd, "w") as f:
                json.dump(man, f, indent=2)
                f.write("\n")
            os.replace(tmp, p)
            return man
        except Exception:
            if os.path.isfile(tmp):
                os.remove(tmp)
            raise
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def load_manifest(project: str) -> dict:
    return _read_manifest_file(project)


def bundle_dir(project: str, key: str) -> str:
    return os.path.join(project, "work", "inspect", ".cache", key)


normalize_relpath = ps.normalize_relpath
resolve_in_bundle = ps.resolve_contained


def iter_bundle_artifact_paths(bundle_root: str) -> list[str]:
    """Relative paths of non-metadata files; any symlink under bundle is rejected."""
    ps.assert_no_symlinks_under(bundle_root)
    found: list[str] = []
    for dirpath, dirnames, files in os.walk(bundle_root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in METADATA_FILES]
        for fn in files:
            if fn in METADATA_FILES:
                continue
            ap = os.path.join(dirpath, fn)
            if ps.lstat_is_symlink(ap):
                raise ValueError(f"symlink_forbidden:{fn}")
            rel = os.path.relpath(ap, bundle_root).replace("\\", "/")
            if not normalize_relpath(rel):
                raise ValueError(f"unsafe_path:{rel}")
            found.append(rel)
    found.sort()
    return found


def validate_bundle_root_safe(project: str, key: str) -> str | None:
    """Ensure inspect cache bundle path and ancestors are not symlinks."""
    rel = _expected_bundle_relpath(key)
    bundle = os.path.join(project, rel)
    proj_real = os.path.realpath(project)
    expected_parent = os.path.realpath(os.path.join(proj_real, "work", "inspect", ".cache"))
    if ps.path_has_symlink_component(bundle):
        return "symlink_forbidden"
    try:
        bundle_real = os.path.realpath(bundle)
    except OSError:
        return "missing_bundle"
    if not bundle_real.startswith(expected_parent + os.sep):
        return "bundle_outside_cache_root"
    return None


def _expected_bundle_relpath(key: str) -> str:
    return os.path.normpath(os.path.join("work", "inspect", ".cache", key)).replace("\\", "/")


def validate_cache_entry(project: str, key: str, ent: dict | None) -> str | None:
    if not ent or not isinstance(ent, dict):
        return "miss"
    rel = ent.get("bundle_dir")
    if not isinstance(rel, str):
        return "invalid_entry"
    exp = _expected_bundle_relpath(key)
    if os.path.normpath(rel).replace("\\", "/") != exp:
        return "bundle_dir_mismatch"
    if ent.get("fingerprint") and ent["fingerprint"] != key:
        return "fingerprint_mismatch"
    bpath = os.path.join(project, rel)
    if not os.path.isdir(bpath):
        return "missing_bundle"
    root_err = validate_bundle_root_safe(project, key)
    if root_err:
        return root_err
    bmeta = os.path.join(bpath, "bundle.json")
    if os.path.isfile(bmeta):
        meta, meta_err = ps.load_json_dict(bmeta)
        if meta_err:
            return f"corrupt_bundle_meta:{meta_err}"
        if meta.get("key") != key:
            return "bundle_meta_mismatch"
        if ent.get("mode") and meta.get("mode") != ent.get("mode"):
            return "bundle_mode_mismatch"
    return None


def _required_listed_in_integrity(bundle_path: str, thorough: bool) -> str | None:
    reqs, err = parse_report_requirements(bundle_path, thorough)
    if err:
        return err
    ipath = os.path.join(bundle_path, "integrity.json")
    data, err = ps.load_json_dict(ipath)
    if err == "missing":
        return "missing_integrity_manifest"
    if err:
        return f"corrupt_integrity_manifest:{err}"
    arts = data.get("artifacts")
    if not isinstance(arts, list):
        return "corrupt_integrity_manifest:invalid_artifacts"
    listed = set()
    for r in arts:
        if not isinstance(r, dict):
            return "corrupt_integrity_manifest:invalid_artifact_row"
        n = normalize_relpath(str(r.get("path", "")))
        if not n:
            return "corrupt_integrity_manifest:unsafe_path"
        listed.add(n)
    for req in reqs:
        if req == "sheet_*.jpg":
            continue
        n = normalize_relpath(req)
        if n and n not in listed:
            return f"required_not_in_manifest:{n}"
    return None


def artifact_manifest(bundle_path: str) -> list[dict]:
    rows = []
    for rel in iter_bundle_artifact_paths(bundle_path):
        fp = os.path.join(bundle_path, rel)
        rows.append({"path": rel, "size": os.path.getsize(fp), "sha256": sha256_file(fp)})
    return rows


def parse_report_requirements(bundle_path: str, thorough: bool) -> tuple[list[str], str | None]:
    """Derive required artifact paths from report.json and mode."""
    reqs = list(REQUIRED_FOR_VISUAL if thorough else REQUIRED_FOR_FULL)
    report_path = os.path.join(bundle_path, "report.json")
    if not os.path.isfile(report_path):
        return reqs, None
    try:
        with open(report_path) as f:
            rep = json.load(f)
    except json.JSONDecodeError:
        return [], "corrupt_report_json"
    if not isinstance(rep, dict):
        return [], "corrupt_report_json"

    if thorough:
        sheets = [
            os.path.basename(p)
            for p in glob.glob(os.path.join(bundle_path, "sheet_*.jpg"))
        ]
        sheets.sort()
        if not sheets:
            reqs.append("sheet_*.jpg")
        else:
            reqs.extend(sheets)

        scenes = rep.get("scenes")
        if scenes is None:
            reqs.append("scenes[]")
        elif isinstance(scenes, list):
            for i, sc in enumerate(scenes):
                if not isinstance(sc, dict):
                    continue
                kf = sc.get("kf")
                if kf and isinstance(kf, str):
                    rel = kf.replace("\\", "/")
                    if normalize_relpath(rel):
                        reqs.append(rel)
                    else:
                        return [], "unsafe_path_in_report"
                elif thorough:
                    fallback = f"keyframes/scene_{sc.get('i', i)}.jpg"
                    if os.path.isfile(os.path.join(bundle_path, fallback)):
                        reqs.append(fallback)
                    else:
                        idx = sc.get("i", i)
                        reqs.append(f"keyframes/scene_{idx}.jpg")

        for flag in rep.get("flags") or []:
            if not isinstance(flag, dict):
                continue
            frame = flag.get("frame")
            if not frame:
                ftype = flag.get("type") or "flag"
                t = flag.get("t", 0)
                frame = f"keyframes/flag_{t}_{ftype}.jpg"
            if isinstance(frame, str):
                rel = frame.replace("\\", "/")
                if not normalize_relpath(rel):
                    return [], "unsafe_path_in_report"
                reqs.append(rel)

    seen = set()
    out = []
    for r in reqs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out, None


def verify_integrity(
    bundle_path: str,
    *,
    expected_key: str | None = None,
    expected_mode: str | None = None,
) -> tuple[bool, str]:
    ipath = os.path.join(bundle_path, "integrity.json")
    data, err = ps.load_json_dict(ipath)
    if err == "missing":
        return False, "missing_integrity_manifest"
    if err:
        return False, f"corrupt_integrity_manifest:{err}"
    if data.get("schema") != CACHE_SCHEMA:
        return False, "schema_mismatch"
    if expected_key and data.get("fingerprint") != expected_key:
        return False, "fingerprint_mismatch"
    if expected_mode and data.get("mode") != expected_mode:
        return False, "mode_mismatch"

    listed = data.get("artifacts")
    if not isinstance(listed, list) or len(listed) == 0:
        on_disk = iter_bundle_artifact_paths(bundle_path)
        if on_disk:
            return False, "empty_integrity_manifest"
        return True, "ok"

    listed_paths: list[str] = []
    for row in listed:
        if not isinstance(row, dict):
            return False, "corrupt_integrity_manifest"
        rel = row.get("path")
        nrel = normalize_relpath(str(rel)) if rel else None
        if not nrel:
            return False, "unsafe_path"
        listed_paths.append(nrel)
        resolved = resolve_in_bundle(bundle_path, nrel)
        if not resolved or not os.path.isfile(resolved):
            return False, f"missing_file:{nrel}"
        if os.path.getsize(resolved) != row.get("size"):
            return False, f"size_mismatch:{nrel}"
        if sha256_file(resolved) != row.get("sha256"):
            return False, f"checksum_mismatch:{nrel}"

    if len(listed_paths) != len(set(listed_paths)):
        return False, "duplicate_manifest_paths"
    on_disk = set(iter_bundle_artifact_paths(bundle_path))
    extra = on_disk - set(listed_paths)
    if extra:
        return False, f"unlisted_artifact:{sorted(extra)[0]}"
    missing = set(listed_paths) - on_disk
    if missing:
        return False, f"missing_file:{sorted(missing)[0]}"
    return True, "ok"


def validate_bundle(
    path: str,
    thorough: bool,
    *,
    cache_key: str | None = None,
    mode: str | None = None,
) -> tuple[list[str], str | None]:
    missing = []
    reqs, report_err = parse_report_requirements(path, thorough)
    if report_err:
        return [], report_err
    for req in reqs:
        if req.startswith("sheet_") and req.endswith("*.jpg"):
            if not glob.glob(os.path.join(path, "sheet_*.jpg")):
                missing.append(req)
            continue
        resolved = resolve_in_bundle(path, req)
        if not resolved or not os.path.isfile(resolved):
            missing.append(req)
    for meta in ("bundle.json", "integrity.json"):
        if not os.path.isfile(os.path.join(path, meta)):
            missing.append(meta)
    if missing:
        return missing, "incomplete_bundle"
    manifest_gap = _required_listed_in_integrity(path, thorough)
    if manifest_gap:
        return [], manifest_gap
    ok, reason = verify_integrity(
        path, expected_key=cache_key, expected_mode=mode if thorough else mode
    )
    if not ok:
        return [], reason
    return [], None


def write_bundle_meta(bundle: str, meta: dict) -> None:
    with open(os.path.join(bundle, "bundle.json"), "w") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")


def write_integrity_manifest(bundle: str, fingerprint_key: str, mode: str) -> None:
    manifest = {
        "schema": CACHE_SCHEMA,
        "fingerprint": fingerprint_key,
        "mode": mode,
        "implementation": implementation_hash(),
        "artifacts": artifact_manifest(bundle),
    }
    with open(os.path.join(bundle, "integrity.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def safe_restore_from_bundle(bundle_path: str, out_dir: str, *, force: bool) -> None:
    """Copy bundle artifacts to out_dir via staging; refuse symlinks; keep dest on failure."""
    ps.assert_no_symlinks_under(bundle_path)
    parent = os.path.dirname(out_dir) or "."
    os.makedirs(parent, exist_ok=True)
    staging = tempfile.mkdtemp(dir=parent, prefix=".inspect-restore-")
    bak = None
    try:
        for rel in iter_bundle_artifact_paths(bundle_path):
            src = resolve_in_bundle(bundle_path, rel)
            if not src or not os.path.isfile(src):
                raise ValueError(f"missing_artifact:{rel}")
            if ps.lstat_is_symlink(src):
                raise ValueError(f"symlink_forbidden:{rel}")
            dest = os.path.join(staging, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
        if os.path.isdir(out_dir) and os.listdir(out_dir):
            if not force:
                raise ValueError("out-dir non-empty")
            bak = out_dir + ".restore-bak"
            if os.path.isdir(bak):
                shutil.rmtree(bak)
            os.rename(out_dir, bak)
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        os.rename(staging, out_dir)
        staging = None
        if bak and os.path.isdir(bak):
            shutil.rmtree(bak)
    except Exception:
        if staging and os.path.isdir(staging):
            shutil.rmtree(staging, ignore_errors=True)
        if bak and os.path.isdir(bak) and not os.path.isdir(out_dir):
            os.rename(bak, out_dir)
        raise


def atomic_install_bundle(src: str, dest: str) -> None:
    """Stage copy, then promote under per-bundle lock; keep prior bundle on failure."""
    parent = os.path.dirname(dest)
    os.makedirs(parent, exist_ok=True)
    token = uuid.uuid4().hex[:12]
    staged = os.path.join(parent, f".bundle-staging-{token}")
    if os.path.exists(staged):
        shutil.rmtree(staged)
    shutil.copytree(src, staged)
    lock_path = dest + ".lock"
    bak = dest + ".bak"
    with open(lock_path, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            if os.path.isdir(dest):
                if os.path.isdir(bak):
                    shutil.rmtree(bak)
                os.rename(dest, bak)
            try:
                os.rename(staged, dest)
            except OSError:
                if os.path.isdir(bak) and not os.path.isdir(dest):
                    os.rename(bak, dest)
                if os.path.isdir(staged):
                    shutil.rmtree(staged)
                raise
            if os.path.isdir(bak):
                shutil.rmtree(bak)
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def cmd_lookup(args):
    key = fingerprint(args.video, args)
    if getattr(args, "for_final", False):
        out = {
            "cache_key": key,
            "hit": False,
            "reason": "final_qa_requires_fresh_run",
            "for_final_qa": True,
            "entry": None,
        }
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)

    project = args.project
    man = load_manifest(project)
    if man.get("_manifest_error"):
        out = {"cache_key": key, "hit": False, "reason": man["_manifest_error"], "entry": None}
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)
    ent = man.get("entries", {}).get(key)
    thorough_required = args.mode == "thorough"
    reason = "miss"
    hit = False
    if ent:
        entry_err = validate_cache_entry(project, key, ent)
        if entry_err and entry_err != "miss":
            out = {"cache_key": key, "hit": False, "reason": entry_err, "entry": ent}
            json.dump(out, sys.stdout, indent=2)
            sys.stdout.write("\n")
            sys.exit(1)
        bpath = os.path.join(project, ent["bundle_dir"])
        missing, integrity_reason = validate_bundle(
            bpath,
            thorough_required,
            cache_key=key,
            mode=args.mode,
        )
        if ent.get("fingerprint") and ent["fingerprint"] != key:
            reason = "fingerprint_mismatch"
        elif ent.get("mode") and ent["mode"] != args.mode:
            reason = "mode_mismatch"
        elif missing:
            reason = f"incomplete_bundle:{','.join(missing)}"
        elif integrity_reason and integrity_reason != "ok":
            reason = integrity_reason
        elif thorough_required and ent.get("mode") != "thorough":
            reason = "not_thorough"
        else:
            hit = True
            reason = "hit"
    out = {
        "cache_key": key,
        "hit": hit,
        "reason": reason,
        "for_final_qa": False,
        "entry": ent,
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if hit else 1)


def cmd_store(args):
    key = fingerprint(args.video, args)
    project = args.project
    src_dir = args.inspect_dir
    if not os.path.isdir(src_dir):
        sys.exit(f"inspect dir not found: {src_dir}")
    dest = bundle_dir(project, key)
    with tempfile.TemporaryDirectory() as staging:
        bundle = os.path.join(staging, "bundle")
        shutil.copytree(src_dir, bundle, dirs_exist_ok=True)
        meta = {
            "key": key,
            "video": os.path.abspath(args.video),
            "mode": args.mode,
            "stored_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        }
        write_bundle_meta(bundle, meta)
        write_integrity_manifest(bundle, key, args.mode)
        missing, err = validate_bundle(bundle, args.mode == "thorough", cache_key=key, mode=args.mode)
        if missing or err:
            sys.exit(f"cannot store incomplete bundle: {missing or err}")
        atomic_install_bundle(bundle, dest)

    entry = {
        "bundle_dir": os.path.relpath(dest, project),
        "mode": args.mode,
        "video": os.path.abspath(args.video),
        "fingerprint": key,
        "reason": "stored",
    }

    def _add(man: dict) -> None:
        man.setdefault("entries", {})[key] = entry

    manifest_transaction(project, _add)
    json.dump({"cache_key": key, "bundle": dest}, sys.stdout, indent=2)
    sys.stdout.write("\n")


def cmd_restore(args):
    if getattr(args, "for_final", False):
        out = {"reason": "final_qa_requires_fresh_run", "restored": False}
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(3)

    key = fingerprint(args.video, args)
    project = args.project
    man = load_manifest(project)
    if man.get("_manifest_error"):
        sys.exit(f"manifest invalid: {man['_manifest_error']}")
    entries = man.get("entries")
    if not isinstance(entries, dict):
        sys.exit("manifest invalid: invalid_entries")
    ent = entries.get(key)
    if not ent:
        sys.exit(2)
    entry_err = validate_cache_entry(project, key, ent)
    if entry_err:
        sys.exit(f"cache entry invalid: {entry_err}")
    src = os.path.join(project, ent["bundle_dir"])
    thorough = args.mode == "thorough"
    missing, integrity_reason = validate_bundle(
        src, thorough, cache_key=key, mode=args.mode
    )
    if missing:
        sys.exit(f"bundle incomplete: {missing}")
    if integrity_reason and integrity_reason != "ok":
        sys.exit(f"bundle integrity failed: {integrity_reason}")
    out_dir = args.out_dir or os.path.join(
        project, "work", "inspect", os.path.splitext(os.path.basename(args.video))[0]
    )
    try:
        safe_restore_from_bundle(src, out_dir, force=bool(args.force))
    except ValueError as exc:
        msg = str(exc)
        if msg == "out-dir non-empty":
            sys.exit("out-dir non-empty; pass --force")
        sys.exit(msg)
    print(out_dir)


def cmd_status(args):
    man = load_manifest(args.project)
    json.dump({"schema": man.get("schema"), "entry_count": len(man.get("entries", {}))}, sys.stdout, indent=2)
    sys.stdout.write("\n")


def add_common(sp):
    sp.add_argument("project")
    sp.add_argument("video")
    sp.add_argument("--mode", default="default")
    sp.add_argument("--start", type=float)
    sp.add_argument("--end", type=float)
    sp.add_argument("--inspect-script", help="work/scripts/video_inspect.py for hash")
    sp.add_argument("--ocr-script")
    sp.add_argument("--config-hash", default="")
    sp.add_argument("--model-id", default="", help="ML model id when inspection uses local models")


def main():
    ap = argparse.ArgumentParser(description="Video inspect artifact cache")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = add_common(sub.add_parser("lookup"))
    s.add_argument("--for-final", action="store_true", help="Final pre-publish QA (always cache miss)")
    s.set_defaults(func=cmd_lookup)

    s = add_common(sub.add_parser("store"))
    s.add_argument("inspect_dir", help="work/inspect/<deliverable>/ with artifacts")
    s.set_defaults(func=cmd_store)

    s = add_common(sub.add_parser("restore"))
    s.add_argument("--out-dir")
    s.add_argument("--for-final", action="store_true", help="Refused for final QA evidence")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_restore)

    s = sub.add_parser("status")
    s.add_argument("project")
    s.set_defaults(func=cmd_status)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()