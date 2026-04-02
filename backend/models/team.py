import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.database.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    startup_id = Column(pgUUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    team_name = Column(String, nullable=False)
    description = Column(Text)

    # Relationships
    startup = relationship("Startup", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(pgUUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    role = Column(String)  # 'developer', 'marketer', etc.

    # Relationships
    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members")
