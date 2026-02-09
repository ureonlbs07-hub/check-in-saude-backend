from pydantic import BaseModel
from typing import List

class CheckinRequest(BaseModel):
    relato: str

class CheckinResponse(BaseModel):
    analysis: str
    common_causes: List[str]
    general_care: List[str]
    alert_signs: List[str]
    disclaimer: str