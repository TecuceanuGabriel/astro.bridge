from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    JSON,
    Boolean,
    NUMERIC,
    BigInteger,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from datetime import datetime

from app.core.db import Base


class Satellite(Base):
    __tablename__ = "satellites"
    
    id = Column(Integer, primary_key=True)
    norad_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(100))
    satellite_number = Column(String(50))
    mission_type = Column(String(100))
    status = Column(String(50), default="active", index=True)
    launch_date = Column(DateTime)
    decay_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TLE(Base):
    __tablename__ = "tle_history"
    
    id = Column(Integer, primary_key=True)
    satellite_id = Column(Integer, ForeignKey("satellites.id", ondelete="CASCADE"), index=True, nullable=False)
    tle_line_1 = Column(Text, nullable=False)
    tle_line_2 = Column(Text, nullable=False)
    epoch = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50), default="space-track")
    
    __table_args__ = (
        UniqueConstraint('satellite_id', 'epoch', name='idx_tle_unique_per_satellite'),
    )