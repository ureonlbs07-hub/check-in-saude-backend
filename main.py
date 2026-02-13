from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse
from ai_service import consultar_ia

app = FastAPI(title="Check-in Saúde Mental API")

# ✅ CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP - libera todos (depois você pode restringir)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "check-in-saude-backend",
        "status": "ok"
    }

@app.get("/health")
def healthcheck():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(data: AnalyzeRequest):
    resposta = consultar_ia(data.relato)
    return AnalyzeResponse(response=resposta)