# Changelog — تبدیلیوں کی فہرست

## 2.0.0

**Breaking:** the file layout and several field names changed. The complete
1.0.0 files are kept in `legacy-v1/`.

### Fixed
- Verse-end marker: ASCII `*` replaced by `۝` in every Arabic field (48 places;
  the old Arabic file counted 98 because `text` repeated `arabic`).

### Structure
- **One copy of the Arabic.** `data/duas.json` holds everything that does not
  depend on language (Arabic, transliteration, repeat, parts, audio). Each
  language file in `data/translations/` now holds only translations.
  Ready-made single-language bundles are generated into `dist/<lang>/duas.json`.
- `text` → `translation`. The Arabic file no longer has a `text` copy of `arabic`.
- Arabic brackets removed where they wrapped the whole item (`( … )`, `(( … )).`):
  181 of 267 items changed; 38 items still start with `(` because they mix
  narration and a quoted dua, and there the `((…))` marks show which words are
  recited. A letter-by-letter check confirms no Arabic or translation letter
  was changed.
- Dua `title` removed. It was the chapter title plus "(n of m)", always in English,
  even in the Urdu file. Use `chapters[].title.<lang>` and `number`.
  (10 duas had a slightly different English wording than their chapter; the
  original is in `legacy-v1/`.)
- Chapter titles for all four languages are in one `title` object.
- `transliteration` lives once in the core instead of being `null` in `ur`/`hi`.
- `translationKind`, `translationSource`, `textKind` moved from every dua to
  each translation file's `meta`.
- `repeat` and `parts[].times` are always integers (≥ 1). `null` is gone;
  it meant "once".
- `null` fields (`parts`, `placeholders`, `audio`, `transliteration`) are omitted
  instead of written as `null`.
- `audio` is flat (`url`, `reciterId`, `durationSeconds`); reciter details are in
  `data/reciters.json`. `hisnmuslimId` moved to the top level of the dua.
- `reference.sourceReference` → `bookRef`; the always-empty `reference.references`
  array was dropped.
- `placeholders` is a list of keys in the core (duplicates removed); the
  instruction text is in each translation file.
- English extras (`recitationOnly`, `guidance`, per-part English) live in
  `translations/en.json`.

### Added
- `scripts/build_dist.py` (validates and builds `dist/` + `index.json`),
  `scripts/migrate_v1_to_v2.py`, `types.ts`, `examples/`.
- `dist/duas.csv` now has all four chapter titles and tags, and opens correctly
  in Excel (UTF-8 with BOM).
