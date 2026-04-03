import uuid
import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime
from backend.database.database import Base
from backend.models.base_types import PortableUUID


class StartupSignal(Base):
    __tablename__ = "startup_signals"

    id                  = Column(PortableUUID, primary_key=True, default=uuid.uuid4, index=True)
    name                = Column(String, index=True, nullable=False)
    domain              = Column(String)
    description         = Column(Text)
    traction_score      = Column(Integer)
    innovation_score    = Column(Integer)
    market_trend_score  = Column(Integer)
    team_strength_score = Column(Integer)
    risk_score          = Column(Integer)
    final_score         = Column(Float)
    created_at          = Column(DateTime, default=datetime.datetime.utcnow)
