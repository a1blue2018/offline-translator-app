#!/usr/bin/env python3
"""Build a compact nb\u2194en word list from Wiktionary (kaikki) + optional FreeDict TEI."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

KAIKKI = Path("dict-src/nb.jsonl")
FREQ_NO = Path("dict-src/no_50k.txt")
FREQ_EN = Path("dict-src/en_50k.txt")
OUT_JS = Path("app/src/main/assets/www/dictionary-data.js")

ALLOW = {
    "noun": "n",
    "verb": "v",
    "adj": "adj",
    "adv": "adv",
    "prep": "prep",
    "pron": "pron",
    "det": "det",
    "conj": "conj",
    "intj": "intj",
    "num": "num",
    "article": "art",
}
HEAD = re.compile(r"^[A-Za-zÆØÅæøåÄÖäö][A-Za-zÆØÅæøåÄÖäö'’\-]*$")
FORM = re.compile(
    r"^(alternative form of|alt form of|plural of|singular of|past tense of|"
    r"present tense of|past participle of|inflection of|misspelling of)",
    re.I,
)
PAREN = re.compile(r"\([^)]*\)")
TEI_POS = {"n": "n", "pn": "n", "v": "v", "adj": "adj", "adv": "adv", "prep": "prep", "pron": "pron", "intj": "intj", "num": "num"}


def freq(path: Path) -> dict[str, int]:
    ranks: dict[str, int] = {}
    if not path.exists():
        return ranks
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        word = line.split()[0].lower() if line.strip() else ""
        if word and word not in ranks:
            ranks[word] = i
    return ranks


def good(word: str) -> bool:
    return bool(word and " " not in word and len(word) <= 32 and HEAD.match(word) and not word.startswith("-"))


def translations(glosses: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in glosses:
        g = PAREN.sub("", raw).strip(" .;,:" )
        if not g or FORM.search(g) or len(g.split()) > 6:
            continue
        for part in re.split(r"[,;/]| or ", g):
            t = re.sub(r"^(to|a|an|the)\s+", "", part.strip(), flags=re.I).strip()
            if not t or len(t) > 40 or t.lower() in seen:
                continue
            seen.add(t.lower())
            out.append(t)
            if len(out) >= 6:
                return out
    return out


def parse_kaikki(ranks: dict[str, int]) -> list[dict]:
    entries: list[dict] = []
    with KAIKKI.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            pos = ALLOW.get(obj.get("pos"))
            word = obj.get("word") or ""
            if not pos or not good(word):
                continue
            glosses: list[str] = []
            for sense in obj.get("senses") or []:
                glosses.extend(sense.get("glosses") or [])
            trans = translations(glosses)
            if not trans:
                continue
            extra = {
                "w": word,
                "p": pos,
                "t": trans[:6],
                "r": ranks.get(word.lower(), 80_000),
                "src": "nb",
            }
            ipa = None
            for sound in obj.get("sounds") or []:
                if sound.get("ipa"):
                    ipa = str(sound["ipa"]).strip()[:48]
                    break
            if ipa:
                extra["ipa"] = ipa if ipa.startswith("/") or ipa.startswith("[") else f"/{ipa}/"
            entries.append(extra)
    return entries


def parse_tei(ranks: dict[str, int], covered: set[str]) -> list[dict]:
    matches = list(Path("dict-src").rglob("*.tei"))
    if not matches:
        return []
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    root = ET.parse(matches[0]).getroot()
    entries: list[dict] = []
    for entry in root.findall(".//tei:entry", ns):
        orth = entry.find("tei:form/tei:orth", ns)
        if orth is None or not orth.text:
            continue
        word = orth.text.strip()
        if not good(word) or word.lower() in covered:
            continue
        pos_el = entry.find("tei:gramGrp/tei:pos", ns)
        pos_raw = (pos_el.text or "").strip().lower() if pos_el is not None else ""
        pos = TEI_POS.get(pos_raw, "n" if not pos_raw else None)
        if not pos:
            continue
        trans: list[str] = []
        seen: set[str] = set()
        for q in entry.findall(".//tei:cit[@type='trans']/tei:quote", ns):
            if not q.text:
                continue
            t = q.text.strip()
            if not t or t.lower() in seen:
                continue
            seen.add(t.lower())
            trans.append(t)
            if len(trans) >= 4:
                break
        if not trans:
            continue
        extra = {
            "w": word,
            "p": pos,
            "t": trans,
            "r": ranks.get(word.lower(), 90_000),
            "src": "en",
        }
        entries.append(extra)
    return entries


def main() -> None:
    nb = parse_kaikki(freq(FREQ_NO))
    covered = {t.lower() for e in nb for t in e["t"]}
    en = parse_tei(freq(FREQ_EN), covered)
    all_entries = nb + en
    all_entries.sort(key=lambda e: (e["r"], e["w"].lower()))
    kept = all_entries[:35_000]
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(kept, ensure_ascii=False, separators=(",", ":"))
    OUT_JS.write_text("window.__ORDBOK_DATA__=" + payload + ";\n", encoding="utf-8")
    words = {e["w"].lower() for e in kept if e["src"] == "nb"}
    print(f"entries={len(kept)} nb={sum(1 for e in kept if e['src']=='nb')} en={sum(1 for e in kept if e['src']=='en')}")
    for w in ("hei", "takk", "hus", "bok"):
        print(f"  {w}: {'OK' if w in words else 'MISSING'}")


if __name__ == "__main__":
    main()
