#!/usr/bin/env python3
"""Content-addressed cache for full video-inspect output directories."""
from __future__ import annotations

import argparse
import fcntl
import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def implementation_hash() -> str:
    return sha256_file(os.path.abspath(__file__))[:16]


def probe_meta(path: str) -> dict:
    """Probe container metadata via ffprobe when available."""
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


def load_manifest(project: str) -> dict:
    p = manifest_path(project)
    if os.path.isfile(p):
        with open(p) as f:
            data = json.load(f)
        if data.get("schema") != CACHE_SCHEMA:
            return {"schema": CACHE_SCHEMA, "entries": {}}
        return data
    return {"schema": CACHE_SCHEMA, "entries": {}}


def save_manifest_atomic(project: str, manifest: dict) -> None:
    manifest["schema"] = CACHE_SCHEMA
    p = manifest_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lock_path = p + ".lock"
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".manifest-")
    try:
        with open(lock_path, "a") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                with os.fdopen(fd, "w") as f:
                    json.dump(manifest, f, indent=2)
                    f.write("\n")
                os.replace(tmp, p)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception:
        if os.path.isfile(tmp):
            os.remove(tmp)
        raise


def bundle_dir(project: str, key: str) -> str:
    return os.path.join(project, "work", "inspect", ".cache", key)


def _safe_relpath(root: str, path: str) -> str | None:
    rel = os.path.relpath(path, root)
    if rel.startswith("..") or os.path.isabs(rel):
        return None
    return rel.replace("\\", "/")


def artifact_manifest(bundle_path: str) -> list[dict]:
    rows = []
    for dirpath, _, files in os.walk(bundle_path):
        for fn in files:
            if fn in METADATA_FILES:
                continue
            ap = os.path.join(dirpath, fn)
            rel = _safe_relpath(bundle_path, ap)
            if not rel:
                raise ValueError(f"unsafe bundle path: {ap}")
            rows.append({"path": rel, "size": os.path.getsize(ap), "sha256": sha256_file(ap)})
    rows.sort(key=lambda r: r["path"])
    return rows


def verify_integrity(bundle_path: str) -> tuple[bool, str]:
    ipath = os.path.join(bundle_path, "integrity.json")
    if not os.path.isfile(ipath):
        return False, "missing_integrity_manifest"
    try:
        with open(ipath) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False, "corrupt_integrity_manifest"
    if data.get("schema") != CACHE_SCHEMA:
        return False, "schema_mismatch"
    for row in data.get("artifacts") or []:
        rel = row.get("path")
        if not rel or ".." in rel:
            return False, "unsafe_path"
        fp = os.path.join(bundle_path, rel)
        if not os.path.isfile(fp):
            return False, f"missing_file:{rel}"
        if os.path.getsize(fp) != row.get("size"):
            return False, f"size_mismatch:{rel}"
        if sha256_file(fp) != row.get("sha256"):
            return False, f"checksum_mismatch:{rel}"
    return True, "ok"


def required_artifacts(bundle_path: str, thorough: bool) -> list[str]:
    reqs = list(REQUIRED_FOR_VISUAL if thorough else REQUIRED_FOR_FULL)
    report_path = os.path.join(bundle_path, "report.json")
    if os.path.isfile(report_path):
        try:
            with open(report_path) as f:
                rep = json.load(f)
            for flag in rep.get("flags") or []:
                if not isinstance(flag, dict):
                    continue
                for key in ("frame", "path", "image"):
                    img = flag.get(key)
                    if img and isinstance(img, str) and ".." not in img:
                        reqs.append(img)
        except (json.JSONDecodeError, OSError):
            pass
    # de-dupe preserving order
    seen = set()
    out = []
    for r in reqs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def validate_bundle(path: str, thorough: bool) -> tuple[list[str], str | None]:
    missing = []
    for req in required_artifacts(path, thorough):
        if not os.path.isfile(os.path.join(path, req)):
            missing.append(req)
    for meta in ("bundle.json", "integrity.json"):
        if not os.path.isfile(os.path.join(path, meta)):
            missing.append(meta)
    if missing:
        return missing, "incomplete_bundle"
    ok, reason = verify_integrity(path)
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
    ent = man.get("entries", {}).get(key)
    thorough_required = args.mode == "thorough"
    reason = "miss"
    hit = False
    if ent:
        bpath = os.path.join(project, ent["bundle_dir"])
        missing, integrity_reason = validate_bundle(bpath, thorough_required)
        if ent.get("fingerprint") and ent["fingerprint"] != key:
            reason = "fingerprint_mismatch"
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


def _atomic_copy_tree(src: str, dest: str) -> None:
    parent = os.path.dirname(dest)
    os.makedirs(parent, exist_ok=True)
    tmp = dest + ".tmp"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.rename(tmp, dest)


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
            "artifacts": sorted(
                n for n in os.listdir(bundle) if not fnmatch.fnmatch(n, ".*")
            ),
        }
        write_bundle_meta(bundle, meta)
        write_integrity_manifest(bundle, key, args.mode)
        missing, _ = validate_bundle(bundle, args.mode == "thorough")
        if missing:
            sys.exit(f"cannot store incomplete bundle: {missing}")
        _atomic_copy_tree(bundle, dest)
    man = load_manifest(project)
    man.setdefault("entries", {})[key] = {
        "bundle_dir": os.path.relpath(dest, project),
        "mode": args.mode,
        "video": os.path.abspath(args.video),
        "fingerprint": key,
        "reason": "stored",
    }
    save_manifest_atomic(project, man)
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
    ent = man.get("entries", {}).get(key)
    if not ent:
        sys.exit(2)
    src = os.path.join(project, ent["bundle_dir"])
    missing, integrity_reason = validate_bundle(src, args.mode == "thorough")
    if missing:
        sys.exit(f"bundle incomplete: {missing}")
    if integrity_reason and integrity_reason != "ok":
        sys.exit(f"bundle integrity failed: {integrity_reason}")
    out_dir = args.out_dir or os.path.join(
        project, "work", "inspect", os.path.splitext(os.path.basename(args.video))[0]
    )
    if os.path.isdir(out_dir) and os.listdir(out_dir) and not args.force:
        sys.exit("out-dir non-empty; pass --force")
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(src):
        if name in METADATA_FILES:
            continue
        sp = os.path.join(src, name)
        dp = os.path.join(out_dir, name)
        if os.path.isdir(sp):
            if os.path.exists(dp):
                shutil.rmtree(dp)
            shutil.copytree(sp, dp)
        else:
            shutil.copy2(sp, dp)
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