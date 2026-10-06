# Duas Dataset — دعاؤں کا ڈیٹاسیٹ (ar · en · ur · hi)

Open, re-buildable dataset of **Hisn al-Muslim (حصن المسلم / Fortress of the Muslim)**
supplications in **Arabic, English, Urdu and Hindi** — 132 chapters, 267 duas —
plus transliteration, repetition counts, topic tags and recitation audio links.

```
data/
├── ar/
│   └── duas.json          # 529 KB — original Arabic (+ transliteration, parts, audio)
├── en/
│   └── duas.json          # 587 KB — English meaning + transliteration + guidance notes
├── ur/
│   └── duas.json          # 497 KB — Urdu meaning  (machine translation — see below)
├── hi/
│   └── duas.json          # 546 KB — Hindi meaning (machine translation — see below)
├── duas.all.json          # every dua, all 4 languages in one flat record
├── duas.csv               # spreadsheet view (one row per dua)
├── index.json             # dataset manifest
└── SOURCES.md             # provenance + licence notes

scripts/
├── fetch_sources.sh       # re-download the upstream sources into _src/
├── build_duas.py          # join + validate + write data/
├── chapter_titles.json    # 132 chapter titles in ar / en / ur / hi (edit here)
└── make_preview.py        # build preview.html

preview.html               # single-file offline browser (data embedded, no network)
```

Rebuild at any time:

```bash
bash scripts/fetch_sources.sh     # download upstream sources into _src/
python3 scripts/build_duas.py     # regenerate data/ (also validates)
python3 scripts/make_preview.py   # regenerate preview.html
```

Browse it locally:

```bash
python3 -m http.server 8000 --bind 0.0.0.0   # then open /preview.html
```

`preview.html` embeds all 267 duas in the four languages, so it works offline and
inside sandboxed iframes: language switcher, full-text search (Arabic/English/Urdu/Hindi),
topic filters, repetition sorting and audio links.

---

## Schema

Every language file is self-describing — `meta` first, then `chapters`:

```jsonc
{
  "meta": {
    "dataset": "duas",
    "version": "1.0.0",
    "language": "ur",                  // ar | en | ur | hi
    "languageNative": "اردو",
    "direction": "rtl",                // rtl for ar/ur, ltr for en/hi
    "book": { "id": "hisn-al-muslim", "title": { "ar": "...", "en": "...", "ur": "...", "hi": "..." }, "author": {} },
    "counts": { "chapters": 132, "duas": 267 },
    "schema": { },                     // field list + explanation of "text"
    "sources": [ ],                    // where each field came from, with licence
    "license": { },
    "attribution": "..."
  },
  "chapters": [
    {
      "id": 68,                                    // chapter number in the printed book
      "title": "Invocations for breaking the fast", // title in THIS file's language
      "titleArabic": "الدعاء عند إفطار الصائم",
      "slug": "invocations-for-breaking-the-fast",
      "tags": ["fasting", "food-and-drink"],        // 19 topic tags (OpenDua)
      "duas": [
        {
          "id": "68-01",               // "<chapter>-<item>", stable across all 4 files
          "number": 1,                 // item number inside the chapter
          "title": "Invocations for breaking the fast (1 of 2)",
          "repeat": 1,                 // how many times to recite (null = once)
          "parts": null,               // or [{arabic, transliteration, en, times}] when split
          "placeholders": null,        // or [{key, instruction}] for {{need}}, {{deceasedName}}
          "reference": { "sourceReference": "176", "references": [] },
          "arabic": "((ذَهَبَ الظَّمَأُ وَابْتَلَّتِ العُرُوقُ، وَثَبَتَ الْأَجْرُ إِنْ شَاءَ اللَّهُ)).",
          "text": "پیاس بجھ گئی، رگیں تر ہو گئیں، اور اللہ نے چاہا تو اجر پکا ہو گیا۔",
          "textKind": "translation",           // arabic-original | translation
          "translationSource": "salahulddin-azkar (hisn_translations/ur.dart)",
          "translationKind": "machine",        // original | human | machine
          "transliteration": "Dhahaba aẓ-ẓamaʾu ...",   // ar + en files only
          "audio": {
            "hisnmuslimId": 176,
            "opendua": { "url": "https://audio.opendua.org/hisn/v0.0.2/OD-176.mp3",
                         "reciter": "Muhammad Jumah", "durationSeconds": 14 }
          }
        }
      ]
    }
  ]
}
```

The `en` file adds two convenience fields:

* `englishRecitationOnly` — OpenDua's CC BY 4.0 English of **only the words to recite**
* `guidance` — the narration/instruction around the dua, kept separate from the recitation

### Using it (examples)

```js
// Node / browser
const ur = await (await fetch("./data/ur/duas.json")).json();
const morning = ur.chapters.find(c => c.id === 27);
morning.duas.forEach(d => console.log(d.repeat, d.text));
```

```python
# Python
import json
hi = json.load(open("data/hi/duas.json", encoding="utf-8"))
by_id = {d["id"]: d for ch in hi["chapters"] for d in ch["duas"]}
print(by_id["1-01"]["text"])        # सोने से जागने की पहली दुआ
```

---

## Coverage

| | ar | en | ur | hi |
|---|---|---|---|---|
| chapters | 132 | 132 | 132 | 132 |
| duas | 267 | 267 | 267 | 267 |
| non-empty text | 267 | 267 | 267 | 267 |
| transliteration | 230 | 230 | — | — |
| recitation audio URL | 230 | 230 | 230 | 230 |
| audio id (hisnmuslim.com) | 266 | 266 | 266 | 266 |
| split into `parts` | 25 | 25 | 25 | 25 |
| `{{placeholder}}` slots | 2 | 2 | 2 | 2 |

* 37 items have no transliteration because they are pure narration/instruction
  (e.g. "the Prophet ﷺ used to say …") with nothing to recite.
* 19 topic tags: prayer-and-the-masjid, protection-and-refuge,
  gatherings-and-greetings, morning-and-evening, sleep-and-waking, travel,
  food-and-drink, fasting, hajj-and-umrah, death-and-the-deceased, illness-and-healing,
  distress-and-anxiety, forgiveness-and-repentance, home-and-family, wudu-and-purification,
  weather-and-nature, dhikr-and-praise, provision-and-debt, knowledge-and-guidance.

---

## ⚠️ Quality & licence — read before shipping

1. **Arabic** — from the printed *Hisn al-Muslim* text as published on hisnmuslim.com
   and mirrored by the upstream repos; cross-checked against the OpenDua edition
   (all 267 items aligned, weakest normalised-Arabic similarity 0.57, caused only by
   OpenDua splitting one item into separately recited parts).
2. **English** — the publisher's hisnmuslim.com translation (human). Mechanical
   cleanup only: whitespace, and the source's `AA` romanisation artefact
   (`AAabdullah → 'abdullah`, `KaAAbah → Ka'bah`). OpenDua's CC BY 4.0 English of the
   recitation part is exposed separately as `englishRecitationOnly`.
3. **Urdu & Hindi are MACHINE translations** (Claude AI), published by
   `ahmedsalahulddin/salahulddin-azkar` and disclosed as such by its author.
   They are readable and complete (267/267) but **not human-reviewed and not
   scholarly**. For any public app, print, or da'wah use, replace them with a
   published translation (e.g. Darussalam's *Hisn ul Muslim* Urdu/Hindi editions,
   or islamdb.pk's Urdu text) and keep the same `id` keys — the build script only
   needs a new source map.
4. **Chapter titles in ur/hi** were rendered for this dataset from the Arabic/English
   titles (`scripts/chapter_titles.json`) — review them too.
5. **Licences:** OpenDua data is **CC BY 4.0** (attribution required); its audio has
   separate terms. `ahmedsalahulddin/salahulddin-azkar` states **no licence** — treat
   its content as "usable with attribution, verify before redistribution".
   `majmoo-io/hisnu-al-muslim-data` (AGPL-3.0) was inspected but is **not** used here.
   Religious source text itself is not claimed by anyone.

Full provenance: [`data/SOURCES.md`](data/SOURCES.md)

---

## اردو میں خلاصہ

یہ ایک اوپن ڈیٹاسیٹ ہے جس میں **حصن المسلم** کی **132 ابواب / 267 دعائیں** چار زبانوں
(عربی، انگریزی، اردو، ہندی) میں موجود ہیں — ہر دعا کے ساتھ عربی متن، ترجمہ، تلفظ
(transliteration)، کتنی بار پڑھنی ہے (`repeat`)، آڈیو لنک اور موضوع کے ٹیگز۔

* **عربی متن** اور **انگریزی ترجمہ** انسانی/مستند ذرائع سے ہیں۔
* **اردو اور ہندی ترجمہ مشینی (machine) ہیں** — اوپن سورس ریپو
  `salahulddin-azkar` سے لیے گئے ہیں اور مصنف نے خود انہیں مشینی قرار دیا ہے۔
  ایپ یا اشاعت میں استعمال سے پہلے کسی مستند شائع شدہ ترجمے (مثلاً دارالسلام کا
  اردو حصن المسلم) سے بدل لیں؛ `id` کی وہی رہے گی تو باقی سسٹم نہیں ٹوٹے گا۔
* دوبارہ بنانے کے لیے: `bash scripts/fetch_sources.sh && python3 scripts/build_duas.py`

---

## Other open-source dua projects worth knowing

| Project | Languages | Notes |
|---|---|---|
| [OpenDua](https://opendua.hdfund.org/) | ar, en, transliteration, audio | 267 Hisn al-Muslim entries, versioned, **CC BY 4.0**, JSON/CSV download + HTTP API |
| [ahmedsalahulddin/salahulddin-azkar](https://github.com/ahmedsalahulddin/salahulddin-azkar) | ar, en + ur, hi, fr, id, ms, tr, bn, ha | all 267 duas; non-English ones are AI translations (disclosed) |
| [majmoo-io/hisnu-al-muslim-data](https://github.com/majmoo-io/hisnu-al-muslim-data) | ar (+ scraping tools) | YAML per chapter, well modelled, **AGPL-3.0** |
| [khalid-hussain/hisnulMuslimDB](https://github.com/khalid-hussain/hisnulMuslimDB) | ar | XML + SQLite + PDF, multi-lingual template |
| [rn0x/Adhkar-json](https://github.com/rn0x/Adhkar-json) / [hisn_almuslim_json](https://github.com/rn0x/hisn_almuslim_json) | ar (+ audio) | Hisn al-Muslim JSON + per-dua MP3s |
| [osamayy/azkar-db](https://github.com/osamayy/azkar-db) | ar | azkar + ruqyah, categorised |
| [Seen-Arabic/Morning-And-Evening-Adhkar-DB](https://github.com/Seen-Arabic/Morning-And-Evening-Adhkar-DB) | ar, en | morning/evening only; JSON/CSV/SQL/SQLite, MIT |
| [mohammed-2-5/islamic-library-data](https://github.com/mohammed-2-5/islamic-library-data) | ar (+ some en) | azkar, famous duas, travel/food/sleep/wudu + Quran, hadith, fonts |
| [riadmonir/dua-api](https://github.com/riadmonir/dua-api) | ar, bn, en | 421 duas / 18 categories, MIT |
| [dev-ahmadbilal/islam.js](https://github.com/dev-ahmadbilal/islam.js) | many | TS package: Quran, 28 tafsirs, hadith, dua & azkar in 134 categories |
| [Kind-Unes/Adhkar-Duaa-Multilingual-Database](https://github.com/Kind-Unes/Adhkar-Duaa-Multilingual-Database) | many | small per-language samples, not the full book |
| [Kaggle: Islamic Dua & Adhkar (72 verified duas)](https://www.kaggle.com/datasets/ahsanneural/islamic-dua-and-adhkar-72-verified-duas) | ar, en, ur, transliteration | 72 duas, hadith-verified, **CC BY 4.0** — good source for *human-checked Urdu* of common duas |

For a human-verified Urdu/Hindi upgrade path, the Kaggle set (CC BY 4.0) and
Darussalam's printed translations are the best starting points.
