from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func

from app.database import Base


class ResearchReport(Base):
    __tablename__ = "research_reports"
    id = Column(Integer, primary_key=True, index=True)
    pending_news_id = Column(Integer, ForeignKey("pending_news.id"), nullable=True)
    title = Column(String(500), nullable=False)
    original_source = Column(String(1000), nullable=True)  # Original source URL
    executive_summary = Column(Text, nullable=True)
    technical_deep_dive = Column(Text, nullable=True)
    vietnam_market_impact = Column(Text, nullable=True)
    strategic_action_items = Column(JSON, nullable=True)  # List[str]
    impact_score = Column(Float, default=5.0)
    sentiment = Column(String(20), default="NEUTRAL")  # POSITIVE|NEUTRAL|NEGATIVE
    tags = Column(JSON, nullable=True)
    raw_analysis = Column(JSON, nullable=True)
    source_citations = Column(JSON, nullable=True)
    # List[str] - URLs used as evidence citations within the report
    # Always contains at least original_source, and optionally extra AI analysis URLs
    # Example: ["https://techcrunch.com/2026/...", "https://reuters.com/..."]
    content_accessible = Column(Boolean, default=True)
    # True  = Jina read original article content - report has real citations
    # False = Inaccessible URL (skipped, no report is generated)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
