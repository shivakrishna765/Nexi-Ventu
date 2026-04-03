import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.database import Base
from backend.models.base_types import PortableUUID


class Application(Base):
    __tablename__ = "applications"

    id         = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    user_id    = Column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    startup_id = Column(PortableUUID, ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    status     = Column(String, default="pending")  # pending / accepted / rejected

    user    = relationship("User", back_populates="applications")
    startup = relationship("Startup", back_populates="applications")
