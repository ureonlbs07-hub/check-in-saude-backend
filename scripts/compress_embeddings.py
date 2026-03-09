import json
import numpy as np

print("Carregando embeddings...")

with open("bible_embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []
refs = []
vectors = []

for item in data:
    refs.append((item["book"], item["chapter"], item["verse"]))
    texts.append(item["text"])
    vectors.append(item["embedding"])

vectors = np.array(vectors, dtype="float32")

print("Salvando formato compacto...")

np.save("bible_vectors.npy", vectors)

with open("bible_refs.json", "w", encoding="utf-8") as f:
    json.dump(
        [{"book": r[0], "chapter": r[1], "verse": r[2], "text": t}
         for r, t in zip(refs, texts)],
        f,
        ensure_ascii=False
    )

print("Compactação concluída.")