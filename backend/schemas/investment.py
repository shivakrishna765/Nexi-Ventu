from pydantic import BaseModel
from datetime import datetime

class InvestmentCreate(BaseModel):
    startup_id: int
    amount: float

class InvestmentResponse(BaseModel):
    id: int
    user_id: int
    startup_id: int
    amount: float
    timestamp: datetime
    
    class Config:
        from_attributes = True
