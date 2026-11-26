"""Shared helpers for the pipeline-tool tests: synthetic audio/video and stub commands. No project media."""
import json
import os
import stat
import subprocess
import sys

import numpy as np
import soundfile as sf

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS = os.path.join(REPO, "tools")
SR = 16000


def tool(rel):
    return os.path.join(TOOLS, rel)


def run(cmd, cwd=None, env=None, check=True, timeout=240):
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, **(env or {})})
    if check and r.returncode:
        raise AssertionError(f"{cmd} -> {r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r


def py(rel, *args, **kw):
    return run([sys.executable, tool(rel), *args], **kw)


def speech_wav(path, spans, duration, sr=SR):
    """Silence (very faint noise) with a loud tone in each [start, end] span."""
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1e-5, int(duration * sr))
    for a, b in spans:
        i, j = int(a * sr), int(b * sr)
        x[i:j] += 0.3 * np.sin(2 * np.pi * 220 * np.arange(j - i) / sr)
    sf.write(path, x, sr)


def ffmpeg(*args):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write(path, text, executable=False):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    if executable:
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
