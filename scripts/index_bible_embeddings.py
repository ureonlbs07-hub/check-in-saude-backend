import json
from openai import OpenAI
import os
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Carregando Bíblia...")

with open("bible/almeida.json", "r", encoding="utf-8") as f:
    bible = json.load(f)

verses = []

print("Gerando embeddings...")

for book in bible:

    book_name = book["name"]

    for chapter_index, chapter in enumerate(book["chapters"], start=1):

        for verse_index, verse_text in enumerate(chapter, start=1):

            text = verse_text.strip()

            if not text:
                continue

            try:

                emb = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )

            except Exception as e:

                print("Erro:", e)
                continue

            verses.append({
                "book": book_name,
                "chapter": chapter_index,
                "verse": verse_index,
                "text": text,
                "embedding": emb.data[0].embedding
            })

            print(f"{book_name} {chapter_index}:{verse_index}")

            # salva progresso a cada 200 versículos
            if len(verses) % 200 == 0:

                print("Salvando progresso...")

                with open("bible_embeddings.json", "w", encoding="utf-8") as f:
                    json.dump(verses, f, ensure_ascii=False)

            time.sleep(0.05)

print("Salvando embeddings finais...")

with open("bible_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(verses, f, ensure_ascii=False)

print("Embeddings salvos com sucesso.")