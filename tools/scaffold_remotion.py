#!/usr/bin/env python3
"""Scaffold work/remotion from templates/remotion-starter."""
from __future__ import annotations

import argparse
import json
import os
import textwrap

TOOLKIT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REMOTION_VERSION_FILE = os.path.join(TOOLKIT, "components", "code", "REMOTION_VERSION")
DEFAULT_VERSION = "4.0.541"


def remotion_version() -> str:
    try:
        with open(REMOTION_VERSION_FILE) as f:
            return f.read().strip() or DEFAULT_VERSION
    except OSError:
        return DEFAULT_VERSION


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def safe_symlink(target: str, link: str) -> None:
    if os.path.lexists(link):
        if os.path.islink(link):
            if os.path.realpath(link) == os.path.realpath(target):
                return
            os.remove(link)
        else:
            raise SystemExit(f"refusing to replace non-symlink {link}")
    os.symlink(target, link)


def scaffold(project: str, aspect: str, force: bool = False) -> str:
    remotion = os.path.join(project, "work", "remotion")
    if os.path.isdir(remotion) and os.listdir(remotion) and not force:
        raise SystemExit(f"refusing to overwrite non-empty {remotion}")
    os.makedirs(remotion, exist_ok=True)
    rv = remotion_version()
    w, h = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    pkg = {
        "name": "video-remotion",
        "private": True,
        "scripts": {
            "start": "remotion studio",
            "build": "remotion bundle",
            "render": "remotion render",
        },
        "dependencies": {
            "remotion": rv,
            "@remotion/cli": rv,
            "@remotion/google-fonts": "^4.0.0",
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "simple-icons": "^14.0.0",
        },
    }
    write(os.path.join(remotion, "package.json"), json.dumps(pkg, indent=2) + "\n")
    write(
        os.path.join(remotion, "remotion.config.ts"),
        textwrap.dedent(
            """\
            import {Config} from '@remotion/cli/config';

            Config.setVideoImageFormat('jpeg');
            Config.setOverwriteOutput(true);
            Config.setConcurrency(4);
            Config.overrideWebpackConfig((c) => ({
              ...c,
              resolve: {...c.resolve, symlinks: false},
            }));
            """
        ),
    )
    write(
        os.path.join(remotion, "tsconfig.json"),
        textwrap.dedent(
            """\
            {
              "compilerOptions": {
                "target": "ES2022",
                "module": "ES2022",
                "jsx": "react-jsx",
                "strict": true,
                "moduleResolution": "bundler",
                "preserveSymlinks": true,
                "esModuleInterop": true,
                "skipLibCheck": true,
                "resolveJsonModule": true,
                "lib": ["ES2022", "DOM"]
              },
              "include": ["src"]
            }
            """
        ),
    )
    pub = os.path.join(remotion, "public")
    src = os.path.join(remotion, "src")
    os.makedirs(os.path.join(pub, "data"), exist_ok=True)
    os.makedirs(os.path.join(src, "lib"), exist_ok=True)
    safe_symlink(os.path.abspath(os.path.join(TOOLKIT, "icons")), os.path.join(pub, "icons"))
    safe_symlink(
        os.path.abspath(os.path.join(TOOLKIT, "components", "code")),
        os.path.join(src, "shared"),
    )
    write(
        os.path.join(src, "theme.ts"),
        f"// Fill from brand.md\nexport const FPS = 30;\nexport const WIDTH = {w};\nexport const HEIGHT = {h};\n",
    )
    write(
        os.path.join(src, "lib", "layout.ts"),
        textwrap.dedent(
            f"""\
            /** Rect helpers for HEAD / FULL / SPLIT — see components/specs/layout-states.md */
            export const CANVAS = {{ width: {w}, height: {h} }};
            export const SAFE = 0.05;
            export type LayoutState = 'HEAD' | 'FULL' | 'SPLIT';
            """
        ),
    )
    write(
        os.path.join(src, "Root.tsx"),
        textwrap.dedent(
            """\
            import React from 'react';
            import {Composition} from 'remotion';
            import {FPS, HEIGHT, WIDTH} from './theme';

            const Placeholder: React.FC = () => null;

            export const RemotionRoot: React.FC = () => (
              <Composition
                id="Main"
                component={Placeholder}
                durationInFrames={30 * FPS}
                fps={FPS}
                width={WIDTH}
                height={HEIGHT}
              />
            );
            """
        ),
    )
    write(
        os.path.join(src, "index.ts"),
        "import { registerRoot } from 'remotion';\nimport { RemotionRoot } from './Root';\n\nregisterRoot(RemotionRoot);\n",
    )
    # Named cues: the library, an empty cue list and its (empty) resolved frames.
    with open(os.path.join(TOOLKIT, "templates", "remotion", "cues.ts"), encoding="utf-8") as f:
        write(os.path.join(src, "lib", "cues.ts"), f.read())
    for name in ("cues.json", "cue_frames.json"):
        write(os.path.join(pub, "data", name), "{}\n")
    write(os.path.join(pub, "data", "trailer_ranges.json"), '{"ranges": []}\n')
    write(os.path.join(pub, "data", ".gitkeep"), "")
    return remotion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--aspect", choices=["9:16", "16:9"], default="9:16")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    print(scaffold(args.project, args.aspect, args.force))


if __name__ == "__main__":
    main()