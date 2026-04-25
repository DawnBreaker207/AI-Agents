from sqlalchemy import Column, Integer, Text, String, DateTime, JSON, Float
from sqlalchemy.sql import func

from database import Base


class ResearchReportModel(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)

    tech_trends = Column(JSON, nullable=True)
    employment_status = Column(JSON, nullable=True)
    job_details = Column(JSON, nullable=True)
    research_articles = Column(JSON, nullable=True)

    impact_score = Column(Float, default=0.0)
    sentiment = Column(String, nullable=True)
    sources = Column(JSON, nullable=True)
    categories = Column(JSON, nullable=True)
    regions = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
