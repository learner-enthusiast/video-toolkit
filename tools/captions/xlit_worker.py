#!/usr/bin/env python3
"""Devanagari -> Roman candidates with AI4Bharat IndicXlit, run inside its own venv (vt-xlit-python).

usage: gpu-run vt-xlit-python tools/captions/xlit_worker.py [--topk 4] in.json out.json
  in.json: ["शब्द", ...]    out.json: {"शब्द": ["shabd", "shabda"], ...}   (best first)
Words only: it never sees or returns timestamps.
"""
import argparse
import json


def indicxlit(words, topk):
    import torch
    from ai4bharat.transliteration import XlitEngine

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available: run through gpu-run (no silent CPU fallback)")
    engine = XlitEngine(src_script_type="indic", beam_width=max(4, topk), rescore=False)
    out = {}
    for word in words:
        result = engine.translit_word(word, lang_code="hi", topk=topk)
        out[word] = [r for r in (result if isinstance(result, list) else result.get("hi", [])) if r]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--topk", type=int, default=4)
    ap.add_argument("infile")
    ap.add_argument("outfile")
    args = ap.parse_args()
    with open(args.infile, encoding="utf-8") as f:
        words = json.load(f)
    result = indicxlit(words, args.topk)
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    print(f"transliterated {len(result)} word(s) with IndicXlit")


if __name__ == "__main__":
    main()
