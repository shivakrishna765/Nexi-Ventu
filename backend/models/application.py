import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    startup_id = Column(pgUUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="pending")  # 'pending', 'accepted', 'rejected'

    # Relationships
    user = relationship("User", back_populates="applications")
    startup = relationship("Startup", back_populates="applications")
