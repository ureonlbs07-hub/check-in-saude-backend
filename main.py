from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest
from ai_service import consultar_ia
from services.bible_service import get_verse

import json

app = FastAPI(title="Bibliame API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "bibliame-backend",
        "status": "ok"
    }


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(data: AnalyzeRequest):

    # chama a IA
    ai_response = consultar_ia(data.relato)

    # garante que virou JSON
    if isinstance(ai_response, str):
        parsed = json.loads(ai_response)
    else:
        parsed = ai_response

    verses = []

    for v in parsed["verses"]:

        text = get_verse(
            v["book"],
            v["chapter"],
            v["verse"]
        )

        verses.append({
            "reference": f'{v["book"]} {v["chapter"]}:{v["verse"]}',
            "text": text
        })

    return {
        "reflection": parsed["analysis"],
        "verses": verses
    }