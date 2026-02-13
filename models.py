from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    relato: str


class AnalyzeResponse(BaseModel):
    response: str