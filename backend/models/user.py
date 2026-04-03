import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Boolean
# Use the generic SQLAlchemy UUID that works with BOTH SQLite and PostgreSQL
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import types
from sqlalchemy.orm import relationship
from backend.database.database import Base


# ── Portable UUID type ─────────────────────────────────────────────────────────
# pgUUID works fine with PostgreSQL. For SQLite we need a String-backed UUID.
# This custom type handles both transparently.
class PortableUUID(types.TypeDecorator):
    """Stores UUIDs as CHAR(36) strings in SQLite, native UUID in PostgreSQL."""
    impl = types.CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(str(value))

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(pgUUID(as_uuid=True))
        return dialect.type_descriptor(types.CHAR(36))


class User(Base):
    __tablename__ = "users"

    id = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)   # nullable for OAuth users
    role = Column(String, default="member")          # founder / investor / seeker / collaborator
    bio = Column(String, nullable=True)
    interests = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    location = Column(String, nullable=True)
    preferred_funding_stage = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships (declared ONCE — duplicates caused SQLAlchemy startup crash)
    startups = relationship("Startup", back_populates="founder", cascade="all, delete-orphan")
    teams = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="investor", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    ideas = relationship("Idea", back_populates="user", cascade="all, delete-orphan")
    chatlogs = relationship("ChatLog", back_populates="user", cascade="all, delete-orphan")
