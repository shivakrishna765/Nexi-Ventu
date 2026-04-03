import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)  # nullable for OAuth users
    role = Column(String, default="member")  # founder / investor / seeker / collaborator / admin
    bio = Column(String, nullable=True)       # skills / domain expertise
    interests = Column(String, nullable=True) # domain interests
    skills = Column(String, nullable=True)    # explicit skills field
    experience_level = Column(String, nullable=True)  # junior / mid / senior
    location = Column(String, nullable=True)
    preferred_funding_stage = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    oauth_provider = Column(String, nullable=True)  # "google" | "linkedin" | null
    oauth_id = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    startups = relationship("Startup", back_populates="founder", cascade="all, delete-orphan")
    teams = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="investor", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    ideas = relationship("Idea", back_populates="user", cascade="all, delete-orphan")
    chatlogs = relationship("ChatLog", back_populates="user", cascade="all, delete-orphan")

    # Relationships
    startups = relationship("Startup", back_populates="founder", cascade="all, delete-orphan")
    teams = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="investor", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    ideas = relationship("Idea", back_populates="user", cascade="all, delete-orphan")
    chatlogs = relationship("ChatLog", back_populates="user", cascade="all, delete-orphan")
