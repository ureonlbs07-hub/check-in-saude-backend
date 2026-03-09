import json
from pathlib import Path

BIBLE_PATH = Path("bible/almeida.json")

with open(BIBLE_PATH, "r", encoding="utf-8-sig") as f:
    BIBLE = json.load(f)

def get_verse(book, chapter, verse):

    for b in BIBLE:

        if b["name"].lower() == book.lower():

            return b["chapters"][chapter-1][verse-1]

    return None