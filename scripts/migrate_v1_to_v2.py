#!/usr/bin/env python3
"""One-time migration: legacy-v1/ (four self-contained per-language files)
-> data/ (one language-neutral core + small per-language translation files).

After this has run, `data/` is the source of truth. Edit data/, then run
scripts/build_dist.py to regenerate dist/ and index.json.

Safety net: every Arabic / translation string is compared (letters only, with
brackets, spaces and full stops removed) before and after cleaning. If any
letter would be lost, the script aborts.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V1 = ROOT / "legacy-v1" / "data"
OUT = ROOT / "data"
LANGS = ["ar", "en", "ur", "hi"]
TERMINATORS = ".۔।"

# Instructions for the two {{placeholder}} slots, in each language.
# English comes from OpenDua; Urdu/Hindi were written for this dataset (short UI
# hints, not scripture) and are marked as such in meta.
PLACEHOLDER_TEXT = {
    "en": None,  # taken from the source data
    "ur": {
        "need": "جس معاملے کے لیے استخارہ کر رہے ہیں اس کا ذکر کریں۔",
        "deceasedName": "فوت شدہ شخص کا نام لیں۔",
    },
    "hi": {
        "need": "जिस काम के लिए इस्तिख़ारा कर रहे हैं उसका ज़िक्र करें।",
        "deceasedName": "मरहूम/मृतक व्यक्ति का नाम लें।",
    },
}


def load(lang):
    with open(V1 / lang / "duas.json", encoding="utf8") as f:
        return json.load(f)


def flat(d):
    return [x for c in d["chapters"] for x in c["duas"]]


def match_close(s, i):
    """Index of the ')' that closes the '(' at s[i], or -1."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "(":
            depth += 1
        elif s[j] == ")":
            depth -= 1
            if depth == 0:
                return j
    return -1


def unwrap(s, keep_terminator):
    """Remove brackets that wrap the *whole* string, e.g. '((text)).' -> 'text'.
    Strings that mix narration and quoted speech are left untouched because the
    brackets there carry meaning."""
    s = s.strip()
    m = re.match(r"^(.*?)([\s" + TERMINATORS + r"]*)$", s, re.S)
    core, tail = m.group(1), m.group(2)
    changed = False
    while core.startswith("(") and match_close(core, 0) == len(core) - 1:
        core = core[1:-1].strip()
        changed = True
    if not changed:
        return s
    if keep_terminator:
        term = next((c for c in tail if c in TERMINATORS), "")
        if term and not core.endswith(tuple(TERMINATORS)):
            core += term
    return core


def letters(s):
    return re.sub(r"[()\s" + TERMINATORS + "]", "", s)


def checked_unwrap(s, keep_terminator, where):
    new = unwrap(s, keep_terminator)
    if letters(new) != letters(s):
        sys.exit(f"LETTER LOSS in {where}: {s!r} -> {new!r}")
    return new


def main():
    v1 = {lang: load(lang) for lang in LANGS}
    ar_ch = v1["ar"]["chapters"]
    ids = [x["id"] for x in flat(v1["ar"])]
    for lang in LANGS:
        assert [x["id"] for x in flat(v1[lang])] == ids, f"id order differs in {lang}"

    # ---------- reciters ----------
    reciters = {}
    for x in flat(v1["ar"]):
        od = (x.get("audio") or {}).get("opendua")
        if od:
            reciters.setdefault(
                od["reciterId"], {"id": od["reciterId"], "name": od["reciter"], "source": od["source"]}
            )

    # ---------- chapters ----------
    chapters = []
    for i, c in enumerate(ar_ch):
        per = {lang: v1[lang]["chapters"][i] for lang in LANGS}
        assert all(per[l]["id"] == c["id"] and per[l]["slug"] == c["slug"] and per[l]["tags"] == c["tags"] for l in LANGS)
        chapters.append(
            {
                "id": c["id"],
                "slug": c["slug"],
                "tags": c["tags"],
                "title": {
                    "ar": c["titleArabic"],
                    "en": per["en"]["title"],
                    "ur": per["ur"]["title"],
                    "hi": per["hi"]["title"],
                },
                "duas": [x["id"] for x in c["duas"]],
            }
        )

    # ---------- core (language-neutral) ----------
    core = []
    for c in ar_ch:
        for x in c["duas"]:
            d = {
                "id": x["id"],
                "chapter": c["id"],
                "number": x["number"],
                "arabic": checked_unwrap(x["arabic"], False, f"arabic {x['id']}"),
            }
            if x.get("transliteration"):
                d["transliteration"] = x["transliteration"]
            d["repeat"] = x["repeat"] if isinstance(x["repeat"], int) and x["repeat"] >= 1 else 1
            if x.get("parts"):
                d["parts"] = [
                    {
                        "arabic": p["arabic"],
                        **({"transliteration": p["transliteration"]} if p.get("transliteration") else {}),
                        "times": p["times"] if isinstance(p.get("times"), int) else 1,
                    }
                    for p in x["parts"]
                ]
            if x.get("placeholders"):
                keys = []
                for p in x["placeholders"]:
                    if p["key"] not in keys:
                        keys.append(p["key"])
                d["placeholders"] = keys
            d["bookRef"] = x["reference"]["sourceReference"]
            a = x.get("audio") or {}
            d["hisnmuslimId"] = a.get("hisnmuslimId")
            od = a.get("opendua")
            if od:
                d["audio"] = {
                    "url": od["url"],
                    "reciterId": od["reciterId"],
                    "durationSeconds": od["durationSeconds"],
                }
            core.append(d)

    # arabic / parts / audio must have been identical in every language file
    base = {x["id"]: x for x in flat(v1["ar"])}
    for lang in ("en", "ur", "hi"):
        for y in flat(v1[lang]):
            b = base[y["id"]]
            assert y["arabic"] == b["arabic"], (lang, y["id"], "arabic")
            assert [(p["arabic"], p["times"]) for p in (y["parts"] or [])] == [
                (p["arabic"], p["times"]) for p in (b["parts"] or [])
            ], (lang, y["id"], "parts")
            assert y["audio"] == b["audio"], (lang, y["id"], "audio")
            assert y["repeat"] == b["repeat"], (lang, y["id"], "repeat")

    # ---------- translations ----------
    translations = {}
    for lang in ("en", "ur", "hi"):
        d = v1[lang]
        items = flat(d)
        sources = {x["translationSource"] for x in items}
        kinds = {x["translationKind"] for x in items}
        assert len(sources) == 1 and len(kinds) == 1, (lang, sources, kinds)
        meta = {
            "language": lang,
            "languageName": d["meta"]["languageName"],
            "languageNative": d["meta"]["languageNative"],
            "direction": d["meta"]["direction"],
            "translationKind": kinds.pop(),
            "translationSource": sources.pop(),
            "chapterTitles": "written for this dataset; needs human review" if lang in ("ur", "hi") else "publisher's English",
        }
        out = {}
        for x in items:
            t = {"translation": checked_unwrap(x["text"], True, f"{lang} {x['id']}")}
            if lang == "en":
                ro = x.get("englishRecitationOnly")
                if ro:
                    ro = checked_unwrap(ro, True, f"en recitationOnly {x['id']}")
                    if ro != t["translation"]:
                        t["recitationOnly"] = ro
                if x.get("guidance"):
                    t["guidance"] = x["guidance"]
                if x.get("parts"):
                    t["parts"] = [p["en"] for p in x["parts"]]
            if x.get("placeholders"):
                instr = {}
                for p in x["placeholders"]:
                    instr[p["key"]] = p["instruction"] if lang == "en" else PLACEHOLDER_TEXT[lang][p["key"]]
                t["placeholders"] = instr
            out[x["id"]] = t
        if lang in ("ur", "hi"):
            meta["placeholderInstructions"] = "written for this dataset (UI hints, not scripture)"
        translations[lang] = {"meta": meta, "items": out}

    # ---------- write ----------
    (OUT / "translations").mkdir(parents=True, exist_ok=True)

    def dump(path, obj):
        with open(path, "w", encoding="utf8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")

    dump(OUT / "chapters.json", chapters)
    dump(OUT / "duas.json", core)
    dump(OUT / "reciters.json", list(reciters.values()))
    for lang, obj in translations.items():
        dump(OUT / "translations" / f"{lang}.json", obj)
    # keep provenance for build_dist.py
    m = v1["ar"]["meta"]
    dump(OUT / "provenance.json", {k: m[k] for k in ("book", "sources", "license", "attribution")})

    still_wrapped = sum(1 for d in core if d["arabic"].startswith("(") or d["arabic"].startswith("(("))
    print(f"chapters={len(chapters)} duas={len(core)} reciters={len(reciters)}")
    print(f"arabic strings still starting with '(' (mixed narration + quote, left as is): {still_wrapped}")


if __name__ == "__main__":
    main()
