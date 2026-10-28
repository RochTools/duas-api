# duas-dataset 2.0.0 — حصن المسلم

132 chapters · 267 duas · ar / en / ur / hi

## Which file do I use? — کون سی فائل؟

| I want… | Use |
|---|---|
| one language, ready to render (chapters nested) | `dist/<lang>/duas.json` |
| every language side by side, flat | `dist/duas.all.json` |
| a spreadsheet | `dist/duas.csv` |
| to edit or extend the data | `data/` (then run `python3 scripts/build_dist.py`) |
| the old 1.0.0 layout | `legacy-v1/` |

## Layout

```
data/
  chapters.json            titles in ar/en/ur/hi + ordered dua ids
  duas.json                language-neutral: arabic, transliteration, repeat, parts, audio
  reciters.json
  translations/{en,ur,hi}.json    id -> translation (+ extras)
dist/                      generated — do not edit by hand
index.json                 map of all files, counts, licence
types.ts                   TypeScript types
examples/                  example.mjs, example.py
scripts/                   build_dist.py, migrate_v1_to_v2.py
```

## One dua (core)

```json
{
  "id": "1-01", "chapter": 1, "number": 1,
  "arabic": "الْحَمْدُ للَّهِ الَّذِي أَحْيَانَا …",
  "transliteration": "Al-ḥamdu li-llāhi …",
  "repeat": 1,
  "bookRef": "1", "hisnmuslimId": 1,
  "audio": { "url": "https://audio.opendua.org/…/OD-001.mp3", "reciterId": "reciter-0001", "durationSeconds": 16 }
}
```

Rules: optional fields are omitted when empty (never `null`, except
`hisnmuslimId`); `repeat` and `parts[].times` are integers ≥ 1; `{{key}}` in
text marks a slot the reader fills in (see `placeholders`).

## Notes

* Verse ends in the Arabic are marked `۝`; Quran quotes are inside `﴿ ﴾`.
  If `۝` shows as a box, use an Arabic font such as Amiri or Scheherazade.
* Urdu and Hindi are **machine translations** (see `translationKind` in
  `data/translations/*.json`); get them reviewed before publishing.
* Licence and credits: `LICENSE`, `SOURCES.md`. Changes from 1.0.0: `CHANGELOG.md`.
