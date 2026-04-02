import uuid
import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class Investment(Base):
    __tablename__ = "investments"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    investor_id = Column(pgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    startup_id = Column(pgUUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # 'pending', 'approved', 'rejected'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    investor = relationship("User", back_populates="investments")
    startup = relationship("Startup", back_populates="investments")
