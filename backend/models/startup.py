import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class Startup(Base):
    __tablename__ = "startups"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    domain = Column(String)  # 'AI', 'Health', etc.
    founder_id = Column(pgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    founder = relationship("User", back_populates="startups")
    teams = relationship("Team", back_populates="startup", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="startup", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="startup", cascade="all, delete-orphan")
