from fastapi import FastAPI
from pydantic import BaseModel
from ai_service import consultar_ia

# Inicialização da API
app = FastAPI(title="Check-in Saúde Mental API")

# ====== MODELS ======

class AnalyzeRequest(BaseModel):
    relato: str

class AnalyzeResponse(BaseModel):
    response: str

# ====== ROUTES ======

@app.get("/")
def healthcheck():
    """
    Healthcheck simples para verificar se a API está online.
    """
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(data: AnalyzeRequest):
    """
    Recebe o relato do usuário e retorna
    uma resposta de apoio psicológico (não médica).
    """
    resposta = consultar_ia(data.relato)
    return {"response": resposta}