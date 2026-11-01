"""python3 examples/example.py"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def read(p):
    return json.loads((root / p).read_text(encoding="utf8"))


chapters = {c["id"]: c for c in read("data/chapters.json")}
duas = read("data/duas.json")
ur = read("data/translations/ur.json")["items"]

dua = next(d for d in duas if d["id"] == "1-01")
print(chapters[dua["chapter"]]["title"]["ur"])
print(dua["arabic"])
print(dua.get("transliteration"))
print(ur[dua["id"]]["translation"])
print("repeat x", dua["repeat"], dua.get("audio", {}).get("url", "(no audio)"))
