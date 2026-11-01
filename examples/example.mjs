// node examples/example.mjs
// Reads the language-neutral core + one translation, and prints a dua.
import { readFileSync } from "node:fs";

const read = (p) => JSON.parse(readFileSync(new URL(`../${p}`, import.meta.url), "utf8"));

const chapters = read("data/chapters.json");
const duas = read("data/duas.json");
const ur = read("data/translations/ur.json").items;

const dua = duas.find((d) => d.id === "1-01");
const chapter = chapters.find((c) => c.id === dua.chapter);

console.log(chapter.title.ur);
console.log(dua.arabic);
console.log(dua.transliteration);
console.log(ur[dua.id].translation);
console.log(`repeat ×${dua.repeat}`, dua.audio?.url ?? "(no audio)");

// Or, if you only need one language, use the ready-made bundle:
const bundle = read("dist/ur/duas.json");
console.log(bundle.chapters[0].title, "→", bundle.chapters[0].duas.length, "duas");
