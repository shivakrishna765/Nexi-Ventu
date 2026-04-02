from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class StartupBase(BaseModel):
    name: str
    domain: str
    description: str
    funding_stage: str
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    traction_score: float = 0.0
    market_score: float = 0.0
    team_score: float = 0.0
    innovation_score: float = 0.0

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

class StartupResponse(StartupBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
