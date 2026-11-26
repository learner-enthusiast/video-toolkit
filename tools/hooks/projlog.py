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
import glob
import json
import os
import re
import sys
import time
import traceback

_HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
_TOOLS_DIR = os.path.abspath(os.path.join(_HOOKS_DIR, ".."))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, os.path.dirname(_TOOLS_DIR))

from tools import pricing, routing_config  # noqa: E402
from tools.project_log_lock import project_log_lock  # noqa: E402
from tools.hooks import transcript_ckpt as tck  # noqa: E402

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


def read_current_project(root):
    """(project, session_id) from .current-project: path on line 1, session on line 2."""
    try:
        with open(os.path.join(root, ".current-project")) as f:
            lines = f.read().split("\n")
    except OSError:
        return None, None
    rel = lines[0].strip() or None
    sid = lines[1].strip() if len(lines) > 1 else ""
    return rel, sid or None


def current_project(root, session_id):
    """The current project, only if this Claude session set it. A leftover from an
    earlier session must not receive this session's prompts."""
    rel, owner = read_current_project(root)
    if not session_id or owner != session_id:
        return None
    return rel if rel and is_project(root, rel) else None


def set_current_project(root, project, session_id):
    with open(os.path.join(root, ".current-project"), "w") as f:
        f.write(f"{project}\n{session_id or ''}\n")


@contextlib.contextmanager
def log_lock(root, project):
    """Canonical project log lock (same as project_state.record-approval)."""
    with project_log_lock(os.path.join(root, project)):
        yield


def capture_project_stage(root, project) -> str:
    try:
        from tools import project_state as pst

        absp = os.path.join(root, project)
        st, err = pst.try_load_state(absp)
        if not err and st and st.get("stage") in pst.STAGES:
            return st["stage"]
    except Exception:
        pass
    return "unknown"


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
        set_current_project(root, project, data.get("session_id"))
    elif not mentioned:
        project = current_project(root, data.get("session_id"))
    now = dt.datetime.now(IST)
    st = {
        "prompt": prompt,
        "started_utc": utc_now_iso(),
        "started_local": now.isoformat(),
        "mentioned": mentioned,
        "project": None,
        "prompt_ref": None,
        "stage": "unknown",
    }
    if project:
        st["stage"] = capture_project_stage(root, project)
        write_header(root, project, st)
    # else: a path to a project that doesn't exist yet; Stop retries once the turn created it
    with open(os.path.join(state_dir(root), f"{sid}.json"), "w") as f:
        json.dump(st, f)


def usage_since(paths, since, main_only=None, seen=None, **kwargs):
    """Incremental transcript scan with full-scan fallback (see transcript_ckpt)."""
    inc = os.environ.get("PROJLOG_INCREMENTAL", "1") != "0"
    checkpoint = kwargs.get("checkpoint")
    if checkpoint is None and kwargs.get("root") and kwargs.get("session_id"):
        checkpoint = tck.load_checkpoint(kwargs["root"], kwargs["session_id"])
    return tck.usage_since(
        paths,
        since,
        main_only,
        seen,
        checkpoint=checkpoint if inc else None,
        incremental=inc,
        session_id=kwargs.get("session_id"),
        stats=kwargs.get("stats"),
    )


usage_since_full = tck.usage_since_full


def fmt(t):
    return (f"input {t['input']:,} · cache write {t['cache_write']:,} · "
            f"cache read {t['cache_read']:,} · output {t['output']:,}")


def _fmt_model_bucket(by_model: dict) -> str:
    parts = []
    for model in sorted(by_model):
        t = by_model[model]
        parts.append(
            f"{model} in {t['input']:,} cw {t['cache_write']:,} cr {t['cache_read']:,} out {t['output']:,}"
        )
    return " · ".join(parts)


def fmt_models_footer(main_models: dict, sub_models: dict) -> str:
    chunks = []
    if main_models:
        chunks.append(f"main: {_fmt_model_bucket(main_models)}")
    combined_sub = dict(sub_models or {})
    if combined_sub:
        chunks.append(f"sub: {_fmt_model_bucket(combined_sub)}")
    if not chunks:
        return ""
    return "; models " + " | ".join(chunks)


def fmt_calls_footer(n_main: int, n_side: int, n_sub: int, by_model: dict) -> str:
    line = f"**Calls:** main {n_main} · sidechain {n_side} · subagents {n_sub}"
    called = {m: n for m, n in by_model.items() if n}
    if called:
        line += "; by model: " + " · ".join(f"{m} {called[m]}" for m in sorted(called))
    return line


def fmt_cost_footer(main_models: dict, sub_models: dict) -> str:
    """Cost-weighted total of the turn; prices and weights come from config/model-routing.json."""
    try:
        combined: dict[str, dict] = {}
        for bucket in (main_models, sub_models):
            for model, t in bucket.items():
                dst = combined.setdefault(model, dict(input=0, cache_write=0, cache_read=0, output=0))
                for key in dst:
                    dst[key] += t.get(key, 0)
        total, unpriced = pricing.weighted_cost(combined, routing_config.load_config())
    except Exception:
        return "**Cost:** not available (routing config unreadable)"
    if total is None:
        return "**Cost:** not available (no price for " + ", ".join(unpriced) + ")"
    return f"**Cost:** weighted USD {total:.4f}"


def _entry_has_committed_tokens(lines: list[str], prompt_ref: str) -> bool:
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == f"**Prompt:** {prompt_ref}":
            start = i
            break
    if start is None:
        return False
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("### Handoff") or lines[i].startswith("## "):
            end = i
            break
    for i in range(start + 1, end):
        ln = lines[i]
        if ln.startswith("**Tokens:**") and "not available" not in ln:
            return True
    return False


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
    fin_idx = None
    for i in range(start + 1, end):
        if lines[i].startswith("**Finished**"):
            fin_idx = i
            break
    footer_lines = ["", *footer.split("\n"), ""]
    if fin_idx is not None:
        del_to = fin_idx + 1
        while del_to < end and lines[del_to].strip():
            del_to += 1
        del lines[fin_idx:del_to]
        end -= del_to - fin_idx
        fin_idx = end
    else:
        fin_idx = end
    lines[fin_idx:fin_idx] = footer_lines
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    with open(log, "w") as f:
        f.write(text if text.endswith("\n") else text + "\n")


def read_json(path):
    with open(path) as f:
        return json.load(f)


def drop_state(sp, started_utc):
    """Remove this turn's state file, unless the next prompt already replaced it."""
    try:
        if read_json(sp).get("started_utc") == started_utc:
            os.remove(sp)
    except (OSError, ValueError):
        pass


def cmd_tokens(data, root):
    sid = data.get("session_id") or "nosession"
    sp = os.path.join(state_dir(root), f"{sid}.json")
    try:
        st = read_json(sp)
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
        set_current_project(root, project, data.get("session_id"))
        write_header(root, project, st)
    project = st["project"]
    started_key = st["started_utc"]
    if os.environ.get("PROJLOG_NO_WAIT") != "1":
        time.sleep(1.0)  # let Claude Code flush the last assistant message
    tp = data.get("transcript_path") or ""
    since = st["started_utc"]
    inc = os.environ.get("PROJLOG_INCREMENTAL", "1") != "0"
    sub_paths = []
    if tp:
        base = tp[:-len(".jsonl")] if tp.endswith(".jsonl") else tp
        sub_paths = glob.glob(os.path.join(base, "subagents", "*.jsonl"))

    idem = tck.turn_idempotency_key(st["started_utc"], st.get("prompt_ref"))
    log_path = os.path.join(root, project, "log.md")

    with tck.checkpoint_lock(root, sid):
        ckpt = tck.load_checkpoint(root, sid)
        if ckpt.pop("_invalid", None):
            ckpt["files"] = {}
            ckpt["logged_ids_global"] = []
        if tck.is_turn_committed(ckpt, idem):
            drop_state(sp, started_key)
            return
        seen: set[str] = set()
        scan_stats: dict = {}
        if tp:
            main, side, main_models, side_models, last, n_main, n_side, scan_stats = tck.scan_parent_transcript(
                tp,
                since,
                seen,
                checkpoint=ckpt if inc else None,
                session_id=sid,
                incremental=inc,
                stats=scan_stats,
            )
        else:
            main, side, main_models, side_models, last, n_main, n_side = (None, None, {}, {}, None, 0, 0)
        sub, sub_models, slast, n_sub, _ = tck.scan_subagent_files(
            sub_paths,
            since,
            seen,
            checkpoint=ckpt if inc else None,
            session_id=sid,
            incremental=inc,
            stats=scan_stats,
        )
        if side and sub:
            for k in sub:
                sub[k] += side[k]
        elif side:
            sub = dict(side)
        sub_combined: dict[str, dict] = {}
        for src in (sub_models or {}, side_models or {}):
            for model, t in src.items():
                dst = sub_combined.setdefault(model, dict(input=0, cache_write=0, cache_read=0, output=0))
                for key in dst:
                    dst[key] += t[key]
        sdlast = None
        if not main:
            main = dict(input=0, cache_write=0, cache_read=0, output=0)
        if not sub:
            sub = dict(input=0, cache_write=0, cache_read=0, output=0)
        started = parse_iso(since)
        fin_iso = max([x for x in (last, slast, sdlast) if x] or [utc_now_iso()])
        finished = parse_iso(fin_iso)
        secs = max(0, int((finished - started).total_seconds()))
        took = f"{secs // 60} m {secs % 60:02d} s" if secs >= 60 else f"{secs} s"
        usage_msgs = (n_main or 0) + (n_side or 0) + (n_sub or 0)
        usage_tokens = sum(main.values()) + sum(sub.values())
        has_usage = usage_msgs > 0 or usage_tokens > 0
        if has_usage:
            tok = f"**Tokens:** {fmt(main)} (main session"
            tok += f"; subagents: {fmt(sub)})" if (n_sub or n_side) else "; subagents: none)"
            tok += fmt_models_footer(main_models or {}, sub_combined)
            tok += "\n" + fmt_calls_footer(n_main or 0, n_side or 0, n_sub or 0,
                                           scan_stats.get("calls_by_model") or {})
            tok += "\n" + fmt_cost_footer(main_models or {}, sub_combined)
        else:
            tok = "**Tokens:** not available (no assistant usage found in the transcript)"
        stage = st.get("stage") or "unknown"
        footer = (
            f"**Finished** {finished.astimezone(IST):%H:%M:%S} · **Took** {took}\n"
            f"**Stage:** {stage}\n{tok}"
        )
        tck.merge_global_logged_ids(ckpt, seen)
        footer_durable = False
        with log_lock(root, project):
            try:
                with open(log_path) as f:
                    lines = f.read().split("\n")
            except OSError:
                lines = []
            already_tokens = _entry_has_committed_tokens(lines, st["prompt_ref"])
            if already_tokens and not has_usage:
                footer_durable = True
            else:
                insert_footer(log_path, st["prompt_ref"], footer)
                footer_durable = True
            if footer_durable:
                tck.mark_turn_committed(
                    ckpt,
                    idem,
                    started_utc=st["started_utc"],
                    prompt_ref=st.get("prompt_ref"),
                    session_id=sid,
                )
                try:
                    tck.save_checkpoint(root, sid, ckpt)
                except Exception as exc:
                    log_err(root, project, f"checkpoint save failed: {exc}")
                    if not already_tokens:
                        log_err(
                            root,
                            project,
                            "turn footer written but checkpoint not saved; retry will reconcile",
                        )
    if os.environ.get("PROJLOG_VERIFY") == "1" and tp:
        rmain, rsub, _, _, _, _, _, _ = tck.collect_usage_reference(tp, sub_paths, since)
        if rmain != main or rsub != sub:
            log_err(root, project, f"incremental verify mismatch: main {rmain}!={main} sub {rsub}!={sub}")
    drop_state(sp, started_key)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    root, project, data = None, None, {}
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
            project = current_project(root, data.get("session_id"))
            log_err(root, project, f"{mode}: " + traceback.format_exc().replace("\n", " | "))
        except Exception:
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
