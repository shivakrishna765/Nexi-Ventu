import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database.database import Base
from backend.models.base_types import PortableUUID


class Team(Base):
    __tablename__ = "teams"

    id         = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    startup_id = Column(PortableUUID, ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    team_name  = Column(String, nullable=False)
    description = Column(Text)

    startup = relationship("Startup", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id      = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(PortableUUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    role    = Column(String)

    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members")
