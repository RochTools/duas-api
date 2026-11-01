#!/usr/bin/env python3
"""Build the ready-to-use files in dist/ and index.json from data/.

    python3 scripts/build_dist.py

data/ is the single source of truth:
  data/chapters.json            chapters, titles in ar/en/ur/hi, ordered dua ids
  data/duas.json                language-neutral dua records (Arabic, transliteration, audio ...)
  data/reciters.json            reciter lookup
  data/translations/<lang>.json id -> translation (+ extras)
  data/provenance.json          book, sources, licence, attribution

The script validates the data first and aborts on any inconsistency.
"""
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DIST = ROOT / "dist"
VERSION = "2.0.0"
LANGS = {
    "ar": {"englishName": "Arabic", "nativeName": "العربية", "direction": "rtl"},
    "en": {"englishName": "English", "nativeName": "English", "direction": "ltr"},
    "ur": {"englishName": "Urdu", "nativeName": "اردو", "direction": "rtl"},
    "hi": {"englishName": "Hindi", "nativeName": "हिन्दी", "direction": "ltr"},
}


def read(path):
    with open(path, encoding="utf8") as f:
        return json.load(f)


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def validate(chapters, duas, reciters, translations):
    problems = []
    ids = [d["id"] for d in duas]
    if len(ids) != len(set(ids)):
        problems.append("duplicate dua ids")
    by_id = {d["id"]: d for d in duas}
    chapter_ids = [c["id"] for c in chapters]
    if len(chapter_ids) != len(set(chapter_ids)):
        problems.append("duplicate chapter ids")
    if len({c["slug"] for c in chapters}) != len(chapters):
        problems.append("duplicate chapter slugs")
    listed = [i for c in chapters for i in c["duas"]]
    if listed != ids:
        problems.append("chapters[].duas does not list every dua once, in order")
    for c in chapters:
        for lang in LANGS:
            if not c["title"].get(lang):
                problems.append(f"chapter {c['id']} has no {lang} title")
        for n, i in enumerate(c["duas"], 1):
            d = by_id.get(i)
            if d is None or d["chapter"] != c["id"] or d["number"] != n:
                problems.append(f"dua {i}: chapter/number mismatch")
    rec = {r["id"] for r in reciters}
    for d in duas:
        if "*" in d["arabic"] or not d["arabic"].strip():
            problems.append(f"{d['id']}: bad arabic")
        if not isinstance(d["repeat"], int) or d["repeat"] < 1:
            problems.append(f"{d['id']}: repeat")
        for p in d.get("parts", []):
            if not isinstance(p["times"], int) or p["times"] < 1:
                problems.append(f"{d['id']}: part times")
        if "audio" in d and d["audio"]["reciterId"] not in rec:
            problems.append(f"{d['id']}: unknown reciter")
        # a slot may sit in the Arabic, in a part, or only in the transliteration
        # (54-01: the Arabic says "لِفُلاَنٍ (بِاسْمِهِ)", the slot is in the transliteration)
        slots = set(re.findall(r"\{\{(\w+)\}\}", d["arabic"] + d.get("transliteration", "")))
        for p in d.get("parts", []):
            slots |= set(re.findall(r"\{\{(\w+)\}\}", p["arabic"] + p.get("transliteration", "")))
        if slots != set(d.get("placeholders", [])):
            problems.append(f"{d['id']}: placeholders {slots} vs {d.get('placeholders')}")
    for lang, t in translations.items():
        if list(t["items"]) != ids:
            problems.append(f"{lang}: translation ids differ from duas")
        for i, item in t["items"].items():
            if not item["translation"].strip() or "*" in item["translation"]:
                problems.append(f"{lang} {i}: bad translation")
            if "parts" in item and len(item["parts"]) != len(by_id[i].get("parts", [])):
                problems.append(f"{lang} {i}: parts length")
            if set(item.get("placeholders", {})) != set(by_id[i].get("placeholders", [])):
                problems.append(f"{lang} {i}: placeholder instructions")
    if problems:
        sys.exit("VALIDATION FAILED:\n  " + "\n  ".join(problems))


def merged_dua(d, lang, translations, reciters):
    out = {"id": d["id"], "number": d["number"], "arabic": d["arabic"]}
    if "transliteration" in d:
        out["transliteration"] = d["transliteration"]
    t = translations.get(lang, {}).get("items", {}).get(d["id"])
    if t:
        out["translation"] = t["translation"]
        for k in ("recitationOnly", "guidance"):
            if k in t:
                out[k] = t[k]
    out["repeat"] = d["repeat"]
    if "parts" in d:
        parts = []
        for n, p in enumerate(d["parts"]):
            q = dict(p)
            if t and "parts" in t:
                q["translation"] = t["parts"][n]
            parts.append(q)
        out["parts"] = parts
    if "placeholders" in d:
        out["placeholders"] = [
            {"key": k, **({"instruction": t["placeholders"][k]} if t and "placeholders" in t else {})}
            for k in d["placeholders"]
        ]
    out["bookRef"] = d["bookRef"]
    out["hisnmuslimId"] = d["hisnmuslimId"]
    if "audio" in d:
        out["audio"] = {**d["audio"], "reciter": reciters[d["audio"]["reciterId"]]["name"]}
    return out


def main():
    chapters = read(DATA / "chapters.json")
    duas = read(DATA / "duas.json")
    reciters_list = read(DATA / "reciters.json")
    reciters = {r["id"]: r for r in reciters_list}
    prov = read(DATA / "provenance.json")
    translations = {l: read(DATA / "translations" / f"{l}.json") for l in LANGS if l != "ar"}
    validate(chapters, duas, reciters_list, translations)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    counts = {"chapters": len(chapters), "duas": len(duas)}
    by_id = {d["id"]: d for d in duas}
    kinds = {"ar": "original", **{l: t["meta"]["translationKind"] for l, t in translations.items()}}

    # ---- dist/<lang>/duas.json : one language, chapters nested ----
    for lang, info in LANGS.items():
        meta = {
            "dataset": "duas",
            "version": VERSION,
            "generatedAt": now,
            "language": lang,
            "languageName": info["englishName"],
            "languageNative": info["nativeName"],
            "direction": info["direction"],
            "translationKind": kinds[lang],
            "book": prov["book"],
            "counts": counts,
            "license": prov["license"],
            "attribution": prov["attribution"],
        }
        if lang != "ar":
            meta["translationSource"] = translations[lang]["meta"]["translationSource"]
        bundle = {
            "meta": meta,
            "chapters": [
                {
                    "id": c["id"],
                    "slug": c["slug"],
                    "title": c["title"][lang],
                    "titleArabic": c["title"]["ar"],
                    "tags": c["tags"],
                    "duas": [merged_dua(by_id[i], lang, translations, reciters) for i in c["duas"]],
                }
                for c in chapters
            ],
        }
        write(DIST / lang / "duas.json", bundle)

    # ---- dist/duas.all.json : flat, every language side by side ----
    ch_by_id = {c["id"]: c for c in chapters}
    flat = []
    for d in duas:
        c = ch_by_id[d["chapter"]]
        row = {
            "id": d["id"],
            "chapter": d["chapter"],
            "number": d["number"],
            "chapterTitle": c["title"],
            "tags": c["tags"],
            "arabic": d["arabic"],
        }
        if "transliteration" in d:
            row["transliteration"] = d["transliteration"]
        row["translation"] = {l: translations[l]["items"][d["id"]]["translation"] for l in translations}
        row["repeat"] = d["repeat"]
        for k in ("parts", "placeholders"):
            if k in d:
                row[k] = d[k]
        row["bookRef"] = d["bookRef"]
        row["hisnmuslimId"] = d["hisnmuslimId"]
        if "audio" in d:
            row["audio"] = {**d["audio"], "reciter": reciters[d["audio"]["reciterId"]]["name"]}
        flat.append(row)
    write(
        DIST / "duas.all.json",
        {
            "meta": {"dataset": "duas", "version": VERSION, "generatedAt": now, "counts": counts,
                     "translationKind": kinds, "license": prov["license"], "attribution": prov["attribution"]},
            "duas": flat,
        },
    )

    # ---- dist/duas.csv : spreadsheet view (UTF-8 with BOM so Excel shows Urdu/Arabic) ----
    cols = ["id", "chapter", "number", "chapter_title_ar", "chapter_title_en", "chapter_title_ur",
            "chapter_title_hi", "tags", "arabic", "transliteration", "en", "ur", "hi", "repeat", "audio_url"]
    with open(DIST / "duas.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in flat:
            w.writerow([
                r["id"], r["chapter"], r["number"],
                r["chapterTitle"]["ar"], r["chapterTitle"]["en"], r["chapterTitle"]["ur"], r["chapterTitle"]["hi"],
                ";".join(r["tags"]), r["arabic"], r.get("transliteration", ""),
                r["translation"]["en"], r["translation"]["ur"], r["translation"]["hi"],
                r["repeat"], r.get("audio", {}).get("url", ""),
            ])

    # ---- index.json ----
    index = {
        "name": "duas-dataset",
        "version": VERSION,
        "generatedAt": now,
        "book": prov["book"],
        "counts": {**counts, "languages": list(LANGS)},
        "data": {
            "chapters": "data/chapters.json",
            "duas": "data/duas.json",
            "reciters": "data/reciters.json",
            "translations": {l: f"data/translations/{l}.json" for l in translations},
        },
        "dist": {
            "perLanguage": {l: f"dist/{l}/duas.json" for l in LANGS},
            "all": "dist/duas.all.json",
            "csv": "dist/duas.csv",
        },
        "languages": {l: {**info, "translationKind": kinds[l]} for l, info in LANGS.items()},
        "legacy": "legacy-v1/ holds the unmodified 1.0.0 files (with the ۝ fix only)",
        "sources": prov["sources"],
        "license": prov["license"],
        "attribution": prov["attribution"],
    }
    write(ROOT / "index.json", index)
    print(f"OK  {counts['chapters']} chapters, {counts['duas']} duas, languages: {', '.join(LANGS)}")


if __name__ == "__main__":
    main()
