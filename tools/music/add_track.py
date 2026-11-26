#!/usr/bin/env python3
"""Put a track I chose into the music library (pipeline/music.md). Tools measure it; no model touches it.

usage: vt-python tools/music/add_track.py <file> --source-url URL --license-type "Uppbeat Premium"
    --license-file proof.pdf --mood "calm,tech" --instrumental [--house] [--credit "exact line"]
    [--id my-track] [--content-id-risk "known risk"] [--allow-vocals]
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.music import analyze, library  # noqa: E402

LOW, KNOWN = "low", "known risk"
# Rips are never licensed. studio.youtube.com is the Audio Library's own download button.
NEVER_SOURCES = ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be", "spotify.com",
                 "open.spotify.com", "soundcloud.com", "www.soundcloud.com")


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def add(args) -> dict:
    if not os.path.isfile(args.file):
        raise SystemExit(f"no such file: {args.file}")
    if not args.license_file or not os.path.isfile(args.license_file):
        raise SystemExit("refused: no license file. A track enters the library only with proof of its license")
    if not args.license_type.strip():
        raise SystemExit("refused: name the license with --license-type")
    if not args.instrumental and not args.allow_vocals:
        raise SystemExit("refused: pass --instrumental (a sung vocal fights my voice)")
    if args.instrumental and args.allow_vocals:
        raise SystemExit("--instrumental and --allow-vocals contradict each other")
    if args.house and not args.instrumental:
        raise SystemExit("refused: a house track must be instrumental")
    url = urlparse(args.source_url)
    if url.scheme not in ("http", "https") or not url.hostname:
        raise SystemExit("refused: --source-url must be the page the track came from")
    if url.hostname in NEVER_SOURCES:
        raise SystemExit(f"refused: {url.hostname} is not a licensed download source (pipeline/music.md)")
    moods = [m.strip() for m in args.mood.split(",") if m.strip()]
    if not moods:
        raise SystemExit("refused: give your own mood tags with --mood")
    track_id = args.id or slug(os.path.splitext(os.path.basename(args.file))[0])
    if not library.ID.match(track_id):
        raise SystemExit(f"bad id {track_id!r}: lower-case letters, digits and hyphens")
    digest = library.sha256(args.file)
    for row in library.rows():
        if row["id"] == track_id or row["sha256"] == digest:
            raise SystemExit(f"already in the library as {row['id']}")
    risk = KNOWN if "pixabay" in url.hostname else args.content_id_risk

    audio = analyze.decode(args.file)
    length = len(audio) / analyze.SR
    lufs, peak = analyze.loudness(args.file)
    beat = analyze.tempo(audio)
    seam = analyze.loop_seam(audio, *beat) if beat else None

    name = track_id + os.path.splitext(args.file)[1].lower()
    proof = track_id + os.path.splitext(args.license_file)[1].lower()
    for folder, source, target in (("tracks", args.file, name), ("licenses", args.license_file, proof)):
        os.makedirs(os.path.join(library.root(), folder), exist_ok=True)
        shutil.copyfile(source, os.path.join(library.root(), folder, target))
    row = {
        "id": track_id, "file": name, "mood": ", ".join(moods),
        "bpm": f"{beat[0]:g}" if beat else library.EMPTY, "length": f"{length:.1f} s",
        "loopable": f"yes @ {seam[1]:.3f} s from {seam[0]:.3f} s" if seam else "no",
        "instrumental": "yes" if args.instrumental else "no (vocals)", "★house": "★" if args.house else library.EMPTY,
        "license": f"{args.license_type.strip()} (licenses/{proof})", "credit": args.credit.strip() or "none",
        "content_id_risk": risk, "source_url": args.source_url, "sha256": digest,
        "LUFS / TP": f"{lufs:.1f} / {peak:.1f}", "used_in": library.EMPTY, "last_used": library.EMPTY,
    }
    library.write(library.rows() + [row])
    return row


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--source-url", required=True)
    ap.add_argument("--license-file")
    ap.add_argument("--license-type", required=True)
    ap.add_argument("--mood", required=True, help="your tags, comma-separated")
    ap.add_argument("--instrumental", action="store_true")
    ap.add_argument("--allow-vocals", action="store_true")
    ap.add_argument("--house", action="store_true")
    ap.add_argument("--credit", default="none", help="the exact attribution line the license asks for")
    ap.add_argument("--id")
    ap.add_argument("--content-id-risk", choices=(LOW, KNOWN), default=LOW)
    return ap


if __name__ == "__main__":
    row = add(parser().parse_args())
    for key in ("id", "bpm", "length", "loopable", "LUFS / TP", "content_id_risk"):
        print(f"{key}: {row[key]}")
