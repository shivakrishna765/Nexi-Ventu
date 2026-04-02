from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    query: str
    budget: Optional[float] = None
    risk: Optional[str] = None
    domains: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
