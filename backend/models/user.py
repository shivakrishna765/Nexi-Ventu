import uuid
import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="member") # "founder", "investor", "member"
    bio = Column(String, nullable=True) # Domain expertise or bio
    interests = Column(String, nullable=True) # Domain interests for investment/teams
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    startups = relationship("Startup", back_populates="founder", cascade="all, delete-orphan")
    teams = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="investor", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    ideas = relationship("Idea", back_populates="user", cascade="all, delete-orphan")
    chatlogs = relationship("ChatLog", back_populates="user", cascade="all, delete-orphan")
