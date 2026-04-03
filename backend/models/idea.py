import uuid
import datetime
from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from backend.database.database import Base
from backend.models.base_types import PortableUUID


class Idea(Base):
    __tablename__ = "ideas"

    id          = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    user_id     = Column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title       = Column(String, nullable=False)
    description = Column(Text)
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="ideas")
