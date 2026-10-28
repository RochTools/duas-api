// TypeScript types for duas-dataset v2.0.0
// Language-neutral core: data/duas.json, data/chapters.json, data/reciters.json
// Translations:          data/translations/<lang>.json
// Ready-made bundles:    dist/<lang>/duas.json, dist/duas.all.json

export type Lang = "ar" | "en" | "ur" | "hi";

export interface LocalizedTitle {
  ar: string;
  en: string;
  ur: string;
  hi: string;
}

/** data/chapters.json  (array) */
export interface Chapter {
  id: number;
  slug: string;
  tags: string[];
  title: LocalizedTitle;
  /** dua ids in reading order, e.g. ["1-01", "1-02"] */
  duas: string[];
}

export interface Part {
  arabic: string;
  transliteration?: string;
  /** how many times this part is recited (1 = once) */
  times: number;
}

export interface Audio {
  url: string;
  reciterId: string;
  durationSeconds: number;
}

/** data/duas.json  (array) */
export interface Dua {
  /** stable key: "<chapter>-<two digit number>" */
  id: string;
  chapter: number;
  /** position inside the chapter, starting at 1 */
  number: number;
  /** Arabic with tashkeel. Verse ends are marked with ۝ and Quran quotes with ﴿ ﴾ */
  arabic: string;
  /** Latin transliteration; may contain {{placeholder}} slots. Absent for pure narration */
  transliteration?: string;
  /** how many times the whole item is recited (1 = once) */
  repeat: number;
  /** present when the item is recited as separate phrases */
  parts?: Part[];
  /** keys of {{slots}} the reader fills in (e.g. "need", "deceasedName") */
  placeholders?: string[];
  /** reference number in the printed Hisn al-Muslim */
  bookRef: string;
  hisnmuslimId: number | null;
  /** absent for the 37 items with no recording */
  audio?: Audio;
}

/** data/reciters.json  (array) */
export interface Reciter {
  id: string;
  name: string;
  source: string;
}

/** data/translations/<lang>.json */
export interface TranslationFile {
  meta: {
    language: Exclude<Lang, "ar">;
    languageName: string;
    languageNative: string;
    direction: "ltr" | "rtl";
    /** "human" | "machine" */
    translationKind: string;
    translationSource: string;
  };
  items: Record<string, TranslationItem>;
}

export interface TranslationItem {
  translation: string;
  /** en only: the English with narration removed, just what is recited */
  recitationOnly?: string;
  /** en only: e.g. "(He begins with his right foot), and says:" */
  guidance?: string;
  /** en only: translation of each entry in Dua.parts, same order */
  parts?: string[];
  /** instruction for each key in Dua.placeholders */
  placeholders?: Record<string, string>;
}

/** dist/<lang>/duas.json: core + that language merged, chapters nested */
export interface Bundle {
  meta: Record<string, unknown>;
  chapters: Array<{
    id: number;
    slug: string;
    title: string;
    titleArabic: string;
    tags: string[];
    duas: BundleDua[];
  }>;
}

export interface BundleDua extends Omit<Dua, "chapter" | "placeholders" | "parts" | "audio"> {
  translation?: string; // absent in the "ar" bundle
  recitationOnly?: string;
  guidance?: string;
  parts?: Array<Part & { translation?: string }>;
  placeholders?: Array<{ key: string; instruction?: string }>;
  audio?: Audio & { reciter: string };
}
