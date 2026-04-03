from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import uuid as _uuid


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    preferred_funding_stage: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    bio: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    preferred_funding_stage: Optional[str] = None
    avatar_url: Optional[str] = None
    is_admin: bool = False
    created_at: datetime

    # Convert UUID → str automatically so Pydantic never chokes on UUID objects
    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v)

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
