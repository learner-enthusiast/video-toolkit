#!/usr/bin/env python3
"""Project-log hooks for Claude Code (pipeline/project-log.md).

  projlog.py prompt   UserPromptSubmit: save the prompt, write the entry header.
  projlog.py tokens   Stop: append Finished / Took / Tokens under that entry.

Reads the hook JSON on stdin. Never prints to stdout (that would land in the
conversation), never exits non-zero; errors go to <project>/work/logs/hooks.log
(or <repo>/.hook-state/hooks.log when no project is known).
"""
import contextlib
import datetime as dt
import fcntl
import glob
import json
import os
import re
import sys
import time
import traceback

IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "IST")
PROJECT_MARKERS = ("log.md", "raw", "script.md", "work")
MENTION = re.compile(r"projects/([^\s`'\"<>()\[\]*]+)")


def repo_root(data):
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    # walk up to the toolkit root (the folder that holds projects/ and CLAUDE.md)
    p = os.path.abspath(root)
    while p != "/":
        if os.path.isdir(os.path.join(p, "projects")) and os.path.isfile(os.path.join(p, "CLAUDE.md")):
            return p
        p = os.path.dirname(p)
    return os.path.abspath(root)


def state_dir(root):
    d = os.path.join(root, ".hook-state")
    os.makedirs(d, exist_ok=True)
    return d


def log_err(root, project, msg):
    try:
        if project:
            d = os.path.join(root, project, "work", "logs")
        else:
            d = state_dir(root)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "hooks.log"), "a") as f:
            f.write(f"{dt.datetime.now(IST):%Y-%m-%d %H:%M:%S} {msg}\n")
    except Exception:
        pass


def is_project(root, rel):
    p = os.path.join(root, rel)
    return os.path.isdir(p) and any(os.path.exists(os.path.join(p, m)) for m in PROJECT_MARKERS)


def resolve_mentions(root, prompt):
    """Return (project, mentioned) for the first projects/<...> path in the prompt.
    project is the longest existing project prefix; mentioned is the raw path."""
    for m in MENTION.finditer(prompt):
        segs = [s for s in m.group(1).rstrip(".,;:").split("/") if s]
        mentioned = "projects/" + "/".join(segs[:2])
        for n in range(len(segs), 0, -1):
            rel = "projects/" + "/".join(segs[:n])
            if is_project(root, rel):
                return rel, mentioned
        return None, mentioned
    return None, None


def current_project(root):
    try:
        rel = open(os.path.join(root, ".current-project")).read().strip()
        return rel if rel and is_project(root, rel) else None
    except OSError:
        return None


@contextlib.contextmanager
def log_lock(root, project):
    """Exclusive lock on the project's log.md (work/logs/.log.lock), so the prompt
    hook's append and the Stop hook's read-modify-write never interleave."""
    d = os.path.join(root, project, "work", "logs")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, ".log.lock"), "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def utc_now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def parse_iso(s):
    return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)


def write_header(root, project, st):
    now = dt.datetime.fromisoformat(st["started_local"])
    pdir = os.path.join(root, project, "work", "prompts")
    os.makedirs(pdir, exist_ok=True)
    name = f"{now:%Y-%m-%d_%H%M%S}.md"
    with open(os.path.join(pdir, name), "w") as f:
        f.write(st["prompt"])
        if not st["prompt"].endswith("\n"):
            f.write("\n")
    title = " ".join(st["prompt"].split())[:60] or "(empty prompt)"
    with log_lock(root, project):
        log = os.path.join(root, project, "log.md")
        lead = ""
        if os.path.exists(log) and os.path.getsize(log):
            with open(log, "rb") as f:
                f.seek(-min(2, os.path.getsize(log)), 2)
                tail = f.read()
            lead = "" if tail.endswith(b"\n\n") else ("\n" if tail.endswith(b"\n") else "\n\n")
        else:
            lead = f"# Log: {project[len('projects/'):]}\n\n"
        with open(log, "a") as f:
            f.write(f"{lead}## {now:%Y-%m-%d %H:%M} IST · {title}\n\n"
                    f"**Prompt:** work/prompts/{name}\n"
                    f"**Started** {now:%H:%M:%S}\n\n")
    st["project"] = project
    st["prompt_ref"] = f"work/prompts/{name}"


def cmd_prompt(data, root):
    prompt = data.get("prompt") or ""
    sid = data.get("session_id") or "nosession"
    project, mentioned = resolve_mentions(root, prompt)
    if project:
        with open(os.path.join(root, ".current-project"), "w") as f:
            f.write(project + "\n")
    elif not mentioned:
        project = current_project(root)
    now = dt.datetime.now(IST)
    st = {"prompt": prompt, "started_utc": utc_now_iso(), "started_local": now.isoformat(),
          "mentioned": mentioned, "project": None, "prompt_ref": None}
    if project:
        write_header(root, project, st)
    # else: a path to a project that doesn't exist yet; Stop retries once the turn created it
    with open(os.path.join(state_dir(root), f"{sid}.json"), "w") as f:
        json.dump(st, f)


def usage_since(paths, since, main_only=None, seen=None):
    """Sum assistant usage (deduped by message id) for entries at/after `since`.
    Pass a shared `seen` set to dedupe across several calls."""
    seen = set() if seen is None else seen
    n0 = len(seen)
    tot = dict(input=0, cache_write=0, cache_read=0, output=0)
    by_model: dict[str, dict] = {}
    last = None
    for p in paths:
        try:
            fh = open(p, "rb")
        except OSError:
            continue
        with fh:
            for raw in fh:
                if b'"assistant"' not in raw:
                    continue
                try:
                    e = json.loads(raw)
                except ValueError:
                    continue
                if e.get("type") != "assistant" or (e.get("timestamp") or "") < since:
                    continue
                if main_only is not None and bool(e.get("isSidechain")) == main_only:
                    continue
                m = e.get("message") or {}
                mid = m.get("id") or e.get("uuid")
                if mid in seen:
                    continue
                seen.add(mid)
                u = m.get("usage") or {}
                model = m.get("model") or "unknown"
                mt = by_model.setdefault(
                    model, dict(input=0, cache_write=0, cache_read=0, output=0)
                )
                for key, src in (
                    ("input", "input_tokens"),
                    ("cache_write", "cache_creation_input_tokens"),
                    ("cache_read", "cache_read_input_tokens"),
                    ("output", "output_tokens"),
                ):
                    v = u.get(src) or 0
                    tot[key] += v
                    mt[key] += v
                last = max(last or "", e["timestamp"])
    return tot, last, len(seen) - n0, by_model


def fmt(t):
    return (f"input {t['input']:,} · cache write {t['cache_write']:,} · "
            f"cache read {t['cache_read']:,} · output {t['output']:,}")


def fmt_models(by_model: dict) -> str:
    if not by_model:
        return ""
    parts = []
    for model in sorted(by_model):
        t = by_model[model]
        parts.append(
            f"{model} in {t['input']:,} cw {t['cache_write']:,} cr {t['cache_read']:,} out {t['output']:,}"
        )
    return "; models: " + " · ".join(parts)


def insert_footer(log, prompt_ref, footer):
    with open(log) as f:
        lines = f.read().split("\n")
    hold = float(os.environ.get("PROJLOG_TEST_HOLD") or 0)
    if hold:  # tests only: widen the read-modify-write window
        time.sleep(hold)
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == f"**Prompt:** {prompt_ref}":
            start = i
    if start is None:
        raise RuntimeError(f"entry for {prompt_ref} not found in log.md")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("### Handoff") or lines[i].startswith("## "):
            end = i
            break
    while end > start + 1 and lines[end - 1].strip() == "":
        end -= 1
    lines[end:end] = ["", *footer.split("\n"), ""]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    with open(log, "w") as f:
        f.write(text if text.endswith("\n") else text + "\n")


def drop_state(sp, started_utc):
    """Remove this turn's state file, unless the next prompt already replaced it."""
    try:
        if json.load(open(sp)).get("started_utc") == started_utc:
            os.remove(sp)
    except (OSError, ValueError):
        pass


def cmd_tokens(data, root):
    sid = data.get("session_id") or "nosession"
    sp = os.path.join(state_dir(root), f"{sid}.json")
    try:
        st = json.load(open(sp))
    except (OSError, ValueError):
        return  # no prompt recorded for this turn (no project)
    if not st.get("project"):
        project = None
        if st.get("mentioned") and is_project(root, st["mentioned"]):
            project = st["mentioned"]
        if not project:
            if st.get("mentioned"):
                log_err(root, None, f"prompt names {st['mentioned']}, which is not a project; prompt not logged")
            drop_state(sp, st["started_utc"])
            return
        with open(os.path.join(root, ".current-project"), "w") as f:
            f.write(project + "\n")
        write_header(root, project, st)
    project = st["project"]
    started_key = st["started_utc"]
    if os.environ.get("PROJLOG_NO_WAIT") != "1":
        time.sleep(1.0)  # let Claude Code flush the last assistant message
    tp = data.get("transcript_path") or ""
    since = st["started_utc"]
    main, last, n_main, main_models = usage_since([tp], since, main_only=True) if tp else (None, None, 0, {})
    sub_paths = []
    if tp:
        sub_paths = glob.glob(os.path.join(tp[:-len(".jsonl")] if tp.endswith(".jsonl") else tp, "subagents", "*.jsonl"))
    sub_seen = set()  # one id set across subagents/*.jsonl and main-transcript sidechain entries
    sub, slast, n_sub, sub_models = usage_since(sub_paths, since, seen=sub_seen)
    side, sdlast, n_side, side_models = (
        usage_since([tp], since, main_only=False, seen=sub_seen) if tp else (None, None, 0, {})
    )
    for k in sub:
        sub[k] += side[k] if side else 0
    merged_models = dict(main_models or {})
    for src in (sub_models or {}, side_models or {}):
        for model, t in src.items():
            dst = merged_models.setdefault(
                model, dict(input=0, cache_write=0, cache_read=0, output=0)
            )
            for key in dst:
                dst[key] += t[key]
    started = parse_iso(since)
    fin_iso = max([x for x in (last, slast, sdlast) if x] or [utc_now_iso()])
    finished = parse_iso(fin_iso)
    secs = max(0, int((finished - started).total_seconds()))
    took = f"{secs // 60} m {secs % 60:02d} s" if secs >= 60 else f"{secs} s"
    if n_main:
        tok = f"**Tokens:** {fmt(main)} (main session"
        tok += f"; subagents: {fmt(sub)})" if (n_sub or n_side) else "; subagents: none)"
        tok += fmt_models(merged_models)
    else:
        tok = "**Tokens:** not available (no assistant usage found in the transcript)"
    footer = (f"**Finished** {finished.astimezone(IST):%H:%M:%S} · **Took** {took}\n{tok}")
    with log_lock(root, project):
        insert_footer(os.path.join(root, project, "log.md"), st["prompt_ref"], footer)
    drop_state(sp, started_key)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    root, project = None, None
    try:
        data = json.loads(sys.stdin.read() or "{}")
        root = repo_root(data)
        if mode == "prompt":
            cmd_prompt(data, root)
        elif mode == "tokens":
            cmd_tokens(data, root)
    except Exception:
        try:
            root = root or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
            project = current_project(root)
            log_err(root, project, f"{mode}: " + traceback.format_exc().replace("\n", " | "))
        except Exception:
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
