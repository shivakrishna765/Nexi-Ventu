from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class StartupBase(BaseModel):
    name: str
    domain: str
    description: str
    funding_stage: Optional[str] = None
    risk_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    traction_score: float = 0.0
    market_score: float = 0.0
    team_score: float = 0.0
    innovation_score: float = 0.0
    location: Optional[str] = None
    required_skills: Optional[str] = None


class StartupCreate(StartupBase):
    pass


class StartupUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    funding_stage: Optional[str] = None
    risk_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    traction_score: Optional[float] = None
    market_score: Optional[float] = None
    team_score: Optional[float] = None
    innovation_score: Optional[float] = None
    location: Optional[str] = None
    required_skills: Optional[str] = None


class StartupResponse(BaseModel):
    id: str
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    funding_stage: Optional[str] = None
    risk_level: Optional[str] = None
    traction_score: float = 0.0
    market_score: float = 0.0
    team_score: float = 0.0
    innovation_score: float = 0.0
    location: Optional[str] = None
    required_skills: Optional[str] = None
    founder_id: Optional[str] = None
    created_at: datetime

    @field_validator("id", "founder_id", mode="before")
    @classmethod
    def coerce_uuid(cls, v):
        return str(v) if v is not None else None

    model_config = {"from_attributes": True}
