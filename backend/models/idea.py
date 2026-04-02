import uuid
import datetime
from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ideas")
