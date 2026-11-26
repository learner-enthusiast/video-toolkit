"""Spoken Hindi numbers -> digits for captions. Tables: languages/hi/numbers.json.

A run of number words becomes digits only when it is clearly a number: it has a multiplier
(sau, hazaar, lakh, crore), a decimal point, a value of `digits_from` or more, or a unit word
follows it. A lone "ek" or "do" is usually not a number in Hindi, so it needs a unit.
"""
from __future__ import annotations

import json
import os

TABLES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "languages", "hi", "numbers.json")


def load_tables(path: str = TABLES_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def word_value(word: str, t: dict) -> int | None:
    if word.isdigit():
        return int(word)
    return t["values"].get(word)


def parse_run(words: list[str], i: int, t: dict) -> tuple[int, float] | None:
    """Longest number starting at words[i] (lower-case, punctuation stripped): (end index, value)."""
    total, current, j, seen, last_multiplier = 0, None, i, False, None
    while j < len(words):
        w = words[j]
        value = word_value(w, t)
        multiplier = t["multipliers"].get(w)
        if value is not None:
            if current is not None:
                break  # two plain numbers in a row ("do teen") are two things, not one
            current = value
        elif multiplier:
            if multiplier == 100:
                current = (1 if current is None else current) * 100
            else:
                if last_multiplier and multiplier >= last_multiplier:
                    break
                total += (1 if current is None else current) * multiplier
                current, last_multiplier = None, multiplier
        else:
            break
        seen = True
        j += 1
        # after a multiplier, a following plain number adds on ("sau paanch" = 105)
        if value is None and multiplier == 100 and j < len(words) and word_value(words[j], t) is not None:
            current += word_value(words[j], t)
            j += 1
    if not seen:
        return None
    number: float = total + (current or 0)
    if j + 1 < len(words) and words[j] in t["point"] and (word_value(words[j + 1], t) or 99) <= 9:
        digits, k = "", j + 1
        while k < len(words) and word_value(words[k], t) is not None and word_value(words[k], t) <= 9:
            digits += str(word_value(words[k], t))
            k += 1
        number, j = float(f"{int(number)}.{digits}"), k
    return j, number


def indian_grouping(n: int) -> str:
    s = str(n)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    return ",".join([head, *parts, tail])


def show(number: float, words: list[str], t: dict) -> str:
    """'50 crore' and '1 lakh' stay readable; everything else uses Indian grouping."""
    if number != int(number):
        return f"{number:g}"
    n = int(number)
    for name, size in (("crore", 10_000_000), ("lakh", 100_000)):
        if n >= size and n % size == 0 and any(t["multipliers"].get(w) == size for w in words):
            return f"{n // size} {name}"
    return indian_grouping(n)


def display_runs(words: list[str], t: dict) -> list[tuple[int, int, str]]:
    """[(start, end, shown)] for the number phrases in `words` that should appear as digits.
    A following percent or rupee word is part of the phrase ("95%", "₹40,000")."""
    out, i = [], 0
    while i < len(words):
        found = parse_run(words, i, t)
        if not found:
            i += 1
            continue
        j, number = found
        run = words[i:j]
        unit = words[j] if j < len(words) else ""
        clear = (any(w in t["multipliers"] for w in run) or number != int(number) or unit in t["units_after"]
                 or (number >= t["digits_from"] and not (len(run) == 1 and run[0].isdigit())))
        if len(run) == 1 and run[0] in t["ambiguous_alone"] and unit not in t["units_after"]:
            clear = False
        if clear:
            text = show(number, run, t)
            if unit in t["percent"]:
                text, j = f"{text}%", j + 1
            elif unit in t["rupee"]:
                text, j = f"₹{text}", j + 1
            out.append((i, j, text))
        i = max(j, i + 1)
    return out
