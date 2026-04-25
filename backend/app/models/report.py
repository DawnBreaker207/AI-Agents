from sqlalchemy import Column, Integer, Text, String, DateTime, JSON
from sqlalchemy.sql import func

from database import Base


class ResearchReportModel(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    summary = Column(Text, nullable=True)
    sources = Column(Text, nullable=True)

    key_points = Column(JSON, nullable=True)
    sentiment = Column(String, nullable=True)

    categories = Column(Text, nullable=True)
    regions = Column(Text, nullable=True)

    token_usage_saved = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
