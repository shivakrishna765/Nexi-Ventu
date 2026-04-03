from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class InvestmentCreate(BaseModel):
    startup_id: str
    amount: float


class InvestmentResponse(BaseModel):
    id: str
    investor_id: str
    startup_id: str
    amount: float
    status: Optional[str] = "pending"
    created_at: datetime

    @field_validator("id", "investor_id", "startup_id", mode="before")
    @classmethod
    def coerce_uuid(cls, v):
        return str(v) if v is not None else None

    model_config = {"from_attributes": True}
