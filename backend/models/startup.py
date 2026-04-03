import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from backend.database.database import Base
from backend.models.base_types import PortableUUID


class Startup(Base):
    __tablename__ = "startups"

    id          = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    name        = Column(String, index=True, nullable=False)
    description = Column(Text)
    domain      = Column(String)
    founder_id  = Column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    funding_stage = Column(String, nullable=True)
    risk_level    = Column(String, nullable=True)
    traction_score   = Column(Float, default=0.0)
    market_score     = Column(Float, default=0.0)
    team_score       = Column(Float, default=0.0)
    innovation_score = Column(Float, default=0.0)
    location      = Column(String, nullable=True)
    required_skills = Column(String, nullable=True)
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    founder      = relationship("User", back_populates="startups")
    teams        = relationship("Team", back_populates="startup", cascade="all, delete-orphan")
    investments  = relationship("Investment", back_populates="startup", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="startup", cascade="all, delete-orphan")
