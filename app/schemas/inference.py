from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class InferenceBase(BaseModel):
    pass

class InferenceCreate(InferenceBase):
    pass

class InferenceResponse(BaseModel):
    id: int
    label: str
    confidence: float
    contamination_score: float
    timestamp: datetime
    nutrition_info: Optional[dict] = None

    class Config:
        from_attributes = True
