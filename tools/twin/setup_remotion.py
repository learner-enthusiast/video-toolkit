#!/usr/bin/env python3
"""Build the twin's Remotion folder around the English code, used read-only.

usage: vt-python tools/twin/setup_remotion.py projects/<name>-hi            create
       vt-python tools/twin/setup_remotion.py projects/<name>-hi --verify   fail if the English code changed
src/, scripts/, the package and config files and node_modules are links to the English project; the
twin has its own public/ and public/data/. Bundlers must not resolve the links to their real paths
(Remotion: resolve.symlinks false, tsc: preserveSymlinks, esbuild: --preserve-symlinks), or the
English code would read the English data.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.twin import common  # noqa: E402

# .env holds REMOTION_BRAND: linked, so the twin renders in the English video's brand
LINKED = ("src", "scripts", ".env", "package.json", "package-lock.json", "remotion.config.ts", "tsconfig.json", "node_modules")
# Made for the Hindi footage; never taken from English.
OWN_MEDIA = {"main.mp4", "voice.wav", "backdrop.jpg"}
OWN_DATA = {"timeline.json", "cue_frames.json", "face.json", "trailer_ranges.json"}


def source_hashes(src: str) -> dict[str, str]:
    out = {}
    for folder, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d != "node_modules")
        for name in sorted(files):
            path = os.path.join(folder, name)
            with open(path, "rb") as f:
                out[os.path.relpath(path, src)] = hashlib.sha256(f.read()).hexdigest()
    return out


def link(target: str, at: str) -> None:
    relative = os.path.relpath(target, os.path.dirname(at))
    if os.path.islink(at):
        if os.readlink(at) == relative:
            return
        os.remove(at)
    elif os.path.exists(at):
        raise SystemExit(f"{at} exists and is not a link: the twin must not hold a copy of the English code")
    os.symlink(relative, at)


def copy_public(src: str, dst: str, skip: set) -> None:
    """Real copies (Remotion doesn't serve linked files); linked folders (icons) stay links."""
    os.makedirs(dst, exist_ok=True)
    for name in sorted(os.listdir(src)):
        source, target = os.path.join(src, name), os.path.join(dst, name)
        if name in skip:
            continue
        if os.path.islink(source) and os.path.isdir(source):
            link(os.path.realpath(source), target)
        elif os.path.isdir(source):
            copy_public(source, target, set())
        else:
            shutil.copyfile(source, target)


def setup(twin: str) -> str:
    english = os.path.join(common.english_of(twin), "work", "remotion")
    if not os.path.isdir(os.path.join(english, "src")):
        raise SystemExit(f"no English Remotion source in {english}")
    root = os.path.join(twin, "work", "remotion")
    os.makedirs(root, exist_ok=True)
    for name in LINKED:
        if os.path.exists(os.path.join(english, name)):
            link(os.path.join(os.path.abspath(english), name), os.path.join(os.path.abspath(root), name))
    copy_public(os.path.join(english, "public"), os.path.join(root, "public"), OWN_MEDIA | {"data"})
    data_in, data_out = os.path.join(english, "public", "data"), os.path.join(root, "public", "data")
    os.makedirs(data_out, exist_ok=True)
    for name in sorted(os.listdir(data_in)):
        if name not in OWN_DATA and os.path.isfile(os.path.join(data_in, name)):
            shutil.copyfile(os.path.join(data_in, name), os.path.join(data_out, name))
    os.makedirs(os.path.join(twin, "work", "twin"), exist_ok=True)
    with open(os.path.join(twin, "work", "twin", "english-src.json"), "w") as f:
        json.dump(source_hashes(os.path.join(english, "src")), f, indent=1)
    return root


def verify(twin: str) -> list[str]:
    root = os.path.join(twin, "work", "remotion")
    problems = [f"{name} is a copy, not a link" for name in ("src", "scripts")
                if os.path.exists(os.path.join(root, name)) and not os.path.islink(os.path.join(root, name))]
    with open(os.path.join(twin, "work", "twin", "english-src.json")) as f:
        before = json.load(f)
    now = source_hashes(os.path.join(common.english_of(twin), "work", "remotion", "src"))
    problems += [f"English src changed since setup: {name}"
                 for name in sorted(set(before) | set(now)) if before.get(name) != now.get(name)]
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("twin")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args(argv)
    if args.verify:
        found = verify(args.twin)
        print("\n".join(found) if found else "English code unchanged and linked")
        return 1 if found else 0
    print(setup(args.twin))
    return 0


if __name__ == "__main__":
    sys.exit(main())
