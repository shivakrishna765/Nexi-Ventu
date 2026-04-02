import uuid
import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from backend.database.database import Base

class StartupSignal(Base):
    __tablename__ = "startup_signals"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, nullable=False)
    domain = Column(String)
    description = Column(Text)
    traction_score = Column(Integer)
    innovation_score = Column(Integer)
    market_trend_score = Column(Integer)
    team_strength_score = Column(Integer)
    risk_score = Column(Integer)
    final_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
