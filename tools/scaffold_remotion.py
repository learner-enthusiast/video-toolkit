#!/usr/bin/env python3
"""Scaffold work/remotion from templates/remotion-starter."""
import argparse
import os
import shutil
import textwrap

TOOLKIT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STARTER = os.path.join(TOOLKIT, "templates", "remotion-starter")
REMOTION_VERSION = "4.0.541"


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def scaffold(project: str, aspect: str) -> None:
    remotion = os.path.join(project, "work", "remotion")
    if os.path.isdir(remotion) and os.listdir(remotion):
        raise SystemExit(f"refusing to overwrite non-empty {remotion}")
    os.makedirs(remotion, exist_ok=True)
    w, h = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    pkg = {
        "name": "video-remotion",
        "private": True,
        "dependencies": {
            "remotion": REMOTION_VERSION,
            "@remotion/cli": REMOTION_VERSION,
            "@remotion/google-fonts": "^4.0.0",
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "simple-icons": "^14.0.0",
        },
    }
    write(
        os.path.join(remotion, "package.json"),
        __import__("json").dumps(pkg, indent=2) + "\n",
    )
    write(
        os.path.join(remotion, "remotion.config.ts"),
        textwrap.dedent(
            f"""\
            import {{Config}} from '@remotion/cli/config';

            Config.setVideoImageFormat('jpeg');
            Config.setOverwriteOutput(true);
            Config.setConcurrency(4);
            Config.overrideWebpackConfig((c) => ({{
              ...c,
              resolve: {{...c.resolve, symlinks: false}},
            }}));
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
                "lib": ["ES2022", "DOM"]
              },
              "include": ["src"]
            }
            """
        ),
    )
    icons_rel = os.path.relpath(os.path.join(TOOLKIT, "icons"), os.path.join(remotion, "public"))
    shared_rel = os.path.relpath(os.path.join(TOOLKIT, "components", "code"), os.path.join(remotion, "src"))
    pub = os.path.join(remotion, "public")
    src = os.path.join(remotion, "src")
    os.makedirs(pub, exist_ok=True)
    os.makedirs(os.path.join(pub, "data"), exist_ok=True)
    os.makedirs(src, exist_ok=True)
    for target, link in [
        (os.path.join(pub, "icons"), os.path.abspath(os.path.join(TOOLKIT, "icons"))),
        (os.path.join(src, "shared"), os.path.abspath(os.path.join(TOOLKIT, "components", "code"))),
    ]:
        if os.path.lexists(target):
            os.remove(target)
        os.symlink(link, target)
    write(
        os.path.join(src, "theme.ts"),
        f"// Fill from brand.md\nexport const FPS = 30;\nexport const WIDTH = {w};\nexport const HEIGHT = {h};\n",
    )
    write(os.path.join(pub, "data", ".gitkeep"), "")
    print(remotion)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--aspect", choices=["9:16", "16:9"], default="9:16")
    args = ap.parse_args()
    scaffold(args.project, args.aspect)


if __name__ == "__main__":
    main()