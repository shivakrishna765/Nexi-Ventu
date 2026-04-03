import uuid
import datetime
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database.database import Base
from backend.models.base_types import PortableUUID


class ChatLog(Base):
    __tablename__ = "chatlogs"

    id        = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    user_id   = Column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    query     = Column(Text)
    response  = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chatlogs")
