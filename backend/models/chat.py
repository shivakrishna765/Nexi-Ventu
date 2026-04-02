import uuid
import datetime
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class ChatLog(Base):
    __tablename__ = "chatlogs"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chatlogs")
