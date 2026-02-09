from fastapi import FastAPI
from pydantic import BaseModel
from ai_service import consultar_ia

app = FastAPI(title="Check-in Saúde Mental API")


class AnalyzeRequest(BaseModel):
    relato: str


class AnalyzeResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(data: AnalyzeRequest):
    resposta = consultar_ia(data.relato)
    return {"response": resposta}