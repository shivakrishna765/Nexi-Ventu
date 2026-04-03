"""
nexus_chat.py
-------------
Pydantic schemas for the Nexus Venture multi-role chatbot API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class NexusChatRequest(BaseModel):
    """
    Request body for the /nexus-chat endpoint.
    The caller can either rely on the authenticated user's stored role/profile
    or override them inline for demo / testing purposes.
    """
    query: str = Field(..., description="Free-text message or question from the user")

    # Optional overrides (useful for frontend role-selector UI)
    role:                    Optional[str] = Field(None, description="investor | founder | seeker | collaborator")
    skills:                  Optional[str] = Field(None, description="Comma-separated skills")
    interests:               Optional[str] = Field(None, description="Comma-separated domain interests")
    experience_level:        Optional[str] = Field(None, description="junior | mid | senior")
    preferred_funding_stage: Optional[str] = Field(None, description="e.g. Seed, Series A")
    location:                Optional[str] = Field(None, description="City name")
    top_n:                   int           = Field(5,    description="Number of recommendations to return")
    use_ai_style:            bool          = Field(True, description="Use Gemini to make response more natural if API key is set")
    memory_turns:            int           = Field(4,    description="How many previous chat turns to use as short memory context")


class MatchResult(BaseModel):
    """A single recommendation result."""
    id:           str
    name:         str
    type:         str          # "startup" | "founder" | "user"
    match_score:  float
    reasons:      List[str]
    domain:       Optional[str] = None
    funding_stage: Optional[str] = None
    skills:       Optional[str] = None
    location:     Optional[str] = None


class NexusChatResponse(BaseModel):
    """Response body for the /nexus-chat endpoint."""
    role:            str
    formatted_text:  str                  # human-readable chatbot output
    results:         List[MatchResult]    # structured data for frontend cards
