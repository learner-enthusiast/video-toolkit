"""Text side of the Hindi caption engine: script lines, matching keys, transliteration, learning.

Nothing here touches a timestamp.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from difflib import SequenceMatcher

from tools.captions import hindi_numbers
from tools.script_beats import TAG

DEVANAGARI = re.compile(r"[ऀ-ॿ]")
STRIP = " \t\"'“”‘’()[]{}<>*_`·—–-…,.?!:;।॥|"
SENTENCE_END = re.compile(r"[.?!।]+$")


# ---------- the script

def spoken_text(rest: str) -> str:
    """The words to be said on a script line after its beat tag(s)."""
    rest = rest.split("→", 1)[0].replace("`", " ")
    quoted = re.findall(r'"([^"]*)"|“([^”]*)”', rest)
    if quoted:
        return " ".join(a or b for a, b in quoted)
    return rest.strip().lstrip("·-–— ").strip()


def script_beats(text: str) -> list[tuple[str, str]]:
    """[(beat id, spoken text)] in script order. A beat's text may continue on following lines up to
    a blank line or heading. Stops at the short-cut section; the Glossary is not script."""
    beats: list[list] = []
    open_beat = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,3}\s+.*(60-second cut|trailer)", stripped, re.I):
            break
        tags = [m for m in TAG.finditer(line) if m["id"]]
        if tags:
            said = spoken_text(line[tags[-1].end():])
            beats.append([tags[-1]["id"], said])
            open_beat = True
        elif not stripped or stripped.startswith(("#", "|", "**", "- ", ">", "<!--")):
            open_beat = False
        elif open_beat:
            beats[-1][1] = f"{beats[-1][1]} {spoken_text(stripped)}".strip()
    return [(beat, said) for beat, said in beats if said]


def tokens(text: str) -> list[str]:
    """Caption tokens: whitespace words without quotes; punctuation-only pieces are dropped."""
    cleaned = re.sub(r'["“”]', "", text).replace("...", " ").replace("…", " ")
    return [t for t in cleaned.split() if t.strip(STRIP)]


def bare(token: str) -> str:
    return unicodedata.normalize("NFC", token.strip(STRIP))


def number_form(token: str) -> str:
    """The form the number tables read: lower-case, no punctuation, no digit commas."""
    t = bare(token).lower()
    return t.replace(",", "") if re.fullmatch(r"[\d,]+", t) else t


# ---------- matching

def key(word: str) -> str:
    """A spelling-tolerant key for romanized Hindi: long vowels, doubled letters, w/v, ph/f, z/j."""
    k = re.sub(r"[^a-z0-9]", "", word.lower())
    for old, new in (("aa", "a"), ("ee", "i"), ("oo", "u"), ("ph", "f"), ("w", "v"), ("z", "j"), ("q", "k"), ("ck", "k")):
        k = k.replace(old, new)
    k = re.sub(r"c(?!h)", "k", k)
    return re.sub(r"(.)\1+", r"\1", k)


class Unit:
    """One thing to match: a word, or a whole number phrase ("teen sau", "300")."""

    def __init__(self, indexes: list[int], forms: list[str], value: float | None = None):
        self.indexes = indexes
        self.forms = forms          # candidate romanizations of the unit
        self.value = value

    @property
    def keys(self) -> set[str]:
        return {key(f) for f in self.forms if key(f)}


def number_units(romans: list[list[str]], tables: dict) -> list[Unit]:
    """Group words into units. `romans[i]` are the candidate romanizations of word i (best first)."""
    best = [number_form(r[0]) if r else "" for r in romans]
    units, i = [], 0
    while i < len(romans):
        found = hindi_numbers.parse_run(best, i, tables)
        if found and (found[0] - i >= 2 or best[i].isdigit()):
            j, value = found
            units.append(Unit(list(range(i, j)), [" ".join(best[i:j])], value))
            i = j
        else:
            units.append(Unit([i], romans[i] or [""]))
            i += 1
    return units


def similarity(a: Unit, b: Unit, tables: dict) -> float:
    def value_of(unit: Unit):
        if unit.value is not None:
            return unit.value
        for form in unit.forms:
            found = hindi_numbers.parse_run([number_form(form)], 0, tables)
            if found:
                return found[1]
        return None

    if a.value is not None or b.value is not None:
        va, vb = value_of(a), value_of(b)
        return 1.0 if va is not None and va == vb else 0.0
    return max((SequenceMatcher(None, x, y).ratio() for x in a.keys for y in b.keys), default=0.0)


def _pair_block(a: list[Unit], b: list[Unit], threshold: float, tables: dict) -> list[tuple[int, int, float]]:
    """Order-preserving pairs inside a block with no exact key match, maximising total similarity."""
    sims = [[similarity(x, y, tables) for y in b] for x in a]
    best = [[0.0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            take = sims[i][j] + best[i + 1][j + 1] if sims[i][j] >= threshold else -1.0
            best[i][j] = max(best[i + 1][j], best[i][j + 1], take)
    pairs, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if sims[i][j] >= threshold and best[i][j] == sims[i][j] + best[i + 1][j + 1]:
            pairs.append((i, j, sims[i][j]))
            i, j = i + 1, j + 1
        elif best[i][j] == best[i + 1][j]:
            i += 1
        else:
            j += 1
    return pairs


def diff(script: list[Unit], heard: list[Unit], threshold: float, tables: dict) -> list[tuple[int | None, int | None, float]]:
    """Merged sequence in spoken order: (script unit, heard unit, similarity). Heard-only entries are
    ad-libs, script-only entries were not said. difflib anchors exact keys (as for English captions);
    the blocks in between are paired by similarity."""
    def code(unit: Unit) -> str:
        return f"#{unit.value}" if unit.value is not None else key(unit.forms[0])

    matcher = SequenceMatcher(None, [code(u) for u in script], [code(u) for u in heard], autojunk=False)
    out: list[tuple[int | None, int | None, float]] = []
    for op, a0, a1, b0, b1 in matcher.get_opcodes():
        if op == "equal":
            out += [(a0 + k, b0 + k, 1.0) for k in range(a1 - a0)]
            continue
        pairs = _pair_block(script[a0:a1], heard[b0:b1], threshold, tables)
        i, j = 0, 0
        for pi, pj, sim in pairs + [(a1 - a0, b1 - b0, 0.0)]:
            out += [(a0 + k, None, 0.0) for k in range(i, pi)]
            out += [(None, b0 + k, 0.0) for k in range(j, pj)]
            if pi < a1 - a0 and pj < b1 - b0:
                out.append((a0 + pi, b0 + pj, sim))
            i, j = pi + 1, pj + 1
    return out


# ---------- dictionary and glossary

def load_json(path: str, default):
    if not os.path.isfile(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_glossary(path: str, script_text: str) -> dict[str, str]:
    """lower-case -> the spelling to show. The project's script Glossary wins over languages/hi."""
    glossary = {k: v for k, v in load_json(path, {}).items() if not k.startswith("_")}
    section = re.search(r"^##\s+Glossary[^\n]*\n(.*?)(?=^##\s|\Z)", script_text, re.M | re.S)
    if section:
        for line in section[1].splitlines():
            if line.strip().startswith("- ") and "<" not in line:
                for term in line.strip()[2:].split(","):
                    for word in term.strip(" `").split():
                        word = word.strip(STRIP)
                        if word and not DEVANAGARI.search(word):
                            glossary[word.lower()] = word
    return glossary


def apply_glossary(token: str, glossary: dict[str, str]) -> str:
    core = token.strip(STRIP)
    shown = glossary.get(core.lower())
    return token.replace(core, shown, 1) if core and shown else token


def spelling(token: str, glossary: dict[str, str]) -> str:
    """The dictionary form of a script word: no punctuation; lower-case unless the glossary cases it."""
    core = bare(token)
    return glossary.get(core.lower(), core.lower())


def learn(dictionary: dict, pairs: list[tuple[str, str]], project: str) -> tuple[list[str], list[dict]]:
    """Add (Devanagari word, script spelling) pairs. Returns (new words, conflicts). A word with two
    spellings is reported and left as it was."""
    seen: dict[str, dict[str, int]] = {}
    for dev, roman in pairs:
        counts = seen.setdefault(dev, {})
        counts[roman] = counts.get(roman, 0) + 1
    learned, conflicts = [], []
    for dev in sorted(seen):
        spellings = seen[dev]
        known = dictionary.get(dev)
        options = sorted(set(spellings) | ({known["roman"]} if known else set()))
        if len(options) > 1:
            conflicts.append({"word": dev, "spellings": options, "in_dictionary": known["roman"] if known else None})
            continue
        roman, count = next(iter(spellings.items()))
        if known:
            known["count"] += count
            known["last_project"] = project
        else:
            dictionary[dev] = {"roman": roman, "count": count, "last_project": project}
            learned.append(dev)
    return learned, conflicts


def save_dictionary(path: str, dictionary: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({k: dictionary[k] for k in sorted(dictionary)}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)
