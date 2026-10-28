# Sources & Licences — ماخذ اور اجازت نامے

Dataset: **Hisn al-Muslim** (حصن المسلم من أذكار الكتاب والسنة) by
Sa'id bin 'Ali bin Wahf al-Qahtani (سعيد بن علي بن وهف القحطاني).
132 chapters / 267 supplications. Build date is recorded in each `meta.generatedAt`.

## Where each field comes from

| Field(s) | Source | Licence | Notes |
|---|---|---|---|
| `arabic`, `repeat`, `hisnmuslimId`, chapters | [ahmedsalahulddin/salahulddin-azkar](https://github.com/ahmedsalahulddin/salahulddin-azkar) → `assets/adhkar/hisn.json` | none stated | That file itself credits the hisnmuslim.com API. Arabic is the standard printed text. |
| `translation` (en) | same file, key `en` | none stated | Publisher's English (hisnmuslim.com / Darussalam lineage). Only mechanical cleanup applied (see below). |
| `translation` (ur) | same repo → `lib/data/hisn_translations/ur.dart` | none stated | **Machine translation (Claude AI)**, disclosed by the repo author. 267/267 keys. |
| `translation` (hi) | same repo → `lib/data/hisn_translations/hi.dart` | none stated | **Machine translation (Claude AI)**, disclosed by the repo author. 267/267 keys. |
| `transliteration`, `recitationOnly`, `guidance`, `parts`, `placeholders`, `tags`, chapter `title` (en), `audio` | [OpenDua](https://opendua.hdfund.org/) catalogue v0.0.4 (2026-09-09) — `https://opendua.hdfund.org/v0.0.4/catalogue.json` | **CC BY 4.0** (data); audio has separate terms | 267 entries, 262 duas, 249 recordings, 132 chapters, 19 tags. |
| chapter titles `ur` / `hi` | written for this dataset in `scripts/chapter_titles.json` | CC BY 4.0 (this compilation) | Rendered from the Arabic/English titles; **needs human review**. |

## How the sources were joined

1. Both sources use the printed book's own chapter numbering (1–132) and item order,
   so entries were paired **per chapter, in order** (267 ↔ 267).
2. Each pairing was verified by comparing **normalised Arabic** (tashkeel, tatweel,
   punctuation and Quran brackets removed; أ/إ/آ→ا, ى→ي, ة→ه, ﷺ expanded):
   `difflib.SequenceMatcher` similarity between the azkar item text and the OpenDua
   recitation text (or the full OpenDua entry text).
   * all 267 pairs ≥ 0.35 → aligned;
   * weakest pair `28-08` = 0.57, and that is only because OpenDua splits
     "SubhanAllah ×33 / Alhamdulillah ×33 / Allahu Akbar ×34" into three parts
     while the azkar text keeps them in one string. Those splits are preserved in `parts`.
3. `audio.url` is taken from the recording attached to the aligned OpenDua
   entry (230 of 267 items have one; reciter: Muhammad Jumah).

## Edits applied to source text

* **Whitespace only** for `ar`, `ur`, `hi` (CRLF→LF, repeated spaces collapsed, trimmed).
* **English:** whitespace + one mechanical romanisation fix. hisnmuslim.com encodes
  hamza/ayn as `AA`, which leaks into the text: `AAabdullah → 'abdullah`,
  `rakAAah → rak'ah`, `KaAAbah → Ka'bah`, `hayya AAalas-salah → hayya 'alas-salah`.
  Case is left exactly as published (so `'abdullah`, not `'Abdullah`).
  Nothing else in the English was rewritten; ayah/verse number markers such as
  `( 285 )` are kept as they appear in the source.
* **No Arabic was altered** beyond whitespace.

## Known gaps

| Gap | Count | Reason |
|---|---|---|
| no `transliteration` | 37 | item is pure narration/instruction — nothing to recite |
| no `audio` | 37 | OpenDua has 249 recordings for 262 duas |
| `hisnmuslimId` is `null` | 1 | not present in the upstream file |
| per-hadith citations | all (the always-empty `references` array was dropped in 2.0.0) | the upstream files carry a book reference number (`sourceReference`) but not per-hadith citations; add them from sunnah.com if you need graded references |

## Reusing this data — attribution

If you redistribute, keep this credit (CC BY 4.0 requires attribution for the OpenDua part):

> Compiled from open sources: OpenDua (opendua.hdfund.org, CC BY 4.0),
> ahmedsalahulddin/salahulddin-azkar, and the hisnmuslim.com English translation.
> Hisn al-Muslim by Sa'id bin 'Ali bin Wahf al-Qahtani.
> Urdu and Hindi texts are machine translations and have not been human-reviewed.

The same strings are embedded in `meta.license` and `meta.attribution` of every
`duas.json`, so a single-file copy still carries its provenance.

## Upgrading Urdu/Hindi to a human translation

Keep the `id` scheme (`"<chapter>-<item>"`) and replace only the `translation`
values in `data/translations/ur.json` (or `hi.json`):

1. Obtain a licensed Urdu/Hindi Hisn al-Muslim translation
   (Darussalam print/PDF, islamdb.pk, or the CC BY 4.0
   [Kaggle 72-dua set](https://www.kaggle.com/datasets/ahsanneural/islamic-dua-and-adhkar-72-verified-duas)
   for the most common duas).
2. Edit the `translation` values and set `meta.translationKind` to `"human"`
   and update `meta.translationSource`.
3. Run `python3 scripts/build_dist.py`. It validates the data and regenerates
   `dist/` and `index.json`.

## v2.0.0 additions (not from the upstream sources)

* Urdu/Hindi `placeholders` instructions (two short UI hints) and the placeholder
  wording were written for this dataset; they are not scripture.
* `data/` is now the source of truth; `legacy-v1/` keeps the 1.0.0 files.
  `scripts/migrate_v1_to_v2.py` shows exactly how 1.0.0 was converted.
