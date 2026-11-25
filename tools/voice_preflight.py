#!/usr/bin/env python3
"""Fast (~5 s) check that the voice cleaner can run, before Prep cleans any recording.

Checks FFmpeg, the WPE libraries, the DeepFilterNet 3 launcher, environment, pinned
versions (from tools/deepfilternet.lock.txt) and cached model. Prints one line per
check and, for any failure, the exact fix. Exit 0 = ready, 1 = not ready.
It never installs or changes anything.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.clean_audio import DEFAULT_DEEPFILTER_PYTHON, deepfilter_command  # noqa: E402

LOCK = ROOT / "tools/deepfilternet.lock.txt"
MODEL_DIR = Path(os.environ.get("DEEPFILTERNET_MODEL_DIR", Path.home() / ".cache/DeepFilterNet/DeepFilterNet3"))
REBUILD = "rebuild the environment: setup.md -> Voice cleaner -> Rebuild (uses tools/deepfilternet.lock.txt)"
PINNED = ("torch", "torchaudio", "DeepFilterNet", "DeepFilterLib", "numpy")


def pinned_versions():
    pins = {}
    for line in LOCK.read_text().splitlines():
        if "==" in line and not line.startswith("#"):
            name, ver = line.strip().split("==", 1)
            pins[name.lower()] = ver
    return pins


def sh(args, timeout=60):
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr).strip()


def checks(executable=None, interpreter=None):
    """Yield (name, ok, detail, fix). `ok` is True, False, or "warn"."""
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    yield "ffmpeg/ffprobe", not missing, "found" if not missing else f"missing: {', '.join(missing)}", "sudo apt install ffmpeg"

    try:
        import numpy, scipy, soundfile  # noqa: F401
        yield "WPE libraries (vt-python)", True, "numpy, scipy, soundfile import", ""
    except ImportError as e:
        yield "WPE libraries (vt-python)", False, str(e), "~/video-toolkit/venv/bin/pip install numpy scipy soundfile"

    try:
        command, backend = deepfilter_command(executable, interpreter)
        code, out = sh(command + ["--version"])
        ok = code == 0 and "0.5.6" in out
        shown = next((l for l in out.splitlines() if "DeepFilterNet" in l and any(c.isdigit() for c in l)), out.splitlines()[-1] if out else "no output")
        yield "DeepFilterNet launcher", ok, f"{backend}: {shown.strip()}", REBUILD
    except (OSError, subprocess.TimeoutExpired) as e:
        yield "DeepFilterNet launcher", False, str(e), REBUILD

    py = Path(interpreter or os.environ.get("DEEPFILTERNET_PYTHON") or DEFAULT_DEEPFILTER_PYTHON).expanduser()
    if not py.is_file() or not os.access(py, os.X_OK) or not py.resolve().exists():
        yield "DeepFilterNet environment", False, f"{py} missing or its base Python is gone (Ubuntu Python upgrade?)", REBUILD
    else:
        probe = ("import json, importlib.metadata as m, torch; "
                 "print(json.dumps({'versions': {p: m.version(p) for p in %r}, 'cuda': torch.cuda.is_available(), "
                 "'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}))" % (PINNED,))
        try:
            code, out = sh([str(py), "-c", probe])
            info = json.loads(out.splitlines()[-1]) if code == 0 else None
        except (subprocess.TimeoutExpired, ValueError, IndexError):
            info = None
        if info is None:
            yield "DeepFilterNet environment", False, (out.splitlines() or ["no output"])[-1][:200], REBUILD
        else:
            pins = pinned_versions()
            drift = [f"{n} {v} (lock {pins.get(n.lower())})" for n, v in info["versions"].items() if pins.get(n.lower()) != v]
            yield "Pinned versions", not drift, "match tools/deepfilternet.lock.txt" if not drift else "drifted: " + ", ".join(drift), REBUILD
            yield ("CUDA for DeepFilterNet", True if info["cuda"] else "warn",
                   info["gpu"] or "not visible: DeepFilterNet will run on the CPU (works; report will warn)",
                   "gpu-run nvidia-smi; see pipeline/gpu.md")

    ckpts = list((MODEL_DIR / "checkpoints").glob("model_*.ckpt*")) if MODEL_DIR.is_dir() else []
    ok = bool(ckpts) and (MODEL_DIR / "config.ini").is_file()
    yield "DeepFilterNet 3 model cache", ok, str(ckpts[0]) if ok else f"no checkpoint/config in {MODEL_DIR}", \
        "re-download (needs internet): deep-filter --model-base-dir DeepFilterNet3 on any short WAV, or rebuild per setup.md"


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--deepfilter-executable"); p.add_argument("--deepfilter-python")
    a = p.parse_args(argv)
    failed = False
    for name, ok, detail, fix in checks(a.deepfilter_executable, a.deepfilter_python):
        mark = "OK  " if ok is True else ("WARN" if ok == "warn" else "FAIL")
        print(f"{mark} {name}: {detail}")
        if ok is False:
            failed = True
            print(f"     fix: {fix}")
    print("voice preflight: " + ("NOT READY - stop Prep and report the FAIL lines; install nothing without approval" if failed else "READY"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
