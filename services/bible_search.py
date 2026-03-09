import json
import numpy as np
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Carregando índice da Bíblia...")

vectors = np.load("bible_vectors.npy")

with open("bible_refs.json", "r", encoding="utf-8") as f:
    refs = json.load(f)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def buscar_versiculos(relato, top_k=5):

    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=relato
    )

    query_vector = np.array(emb.data[0].embedding)

    scores = []

    for i, vec in enumerate(vectors):

        score = cosine_similarity(query_vector, vec)

        scores.append((score, i))

    scores.sort(reverse=True)

    resultados = []

    for score, idx in scores[:top_k]:

        resultados.append({
            "book": refs[idx]["book"],
            "chapter": refs[idx]["chapter"],
            "verse": refs[idx]["verse"],
            "text": refs[idx]["text"],
            "score": float(score)
        })

    return resultados