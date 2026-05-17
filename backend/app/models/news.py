from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from app.database import Base

class PendingNews(Base):
    __tablename__ = "pending_news"
    id             = Column(Integer, primary_key=True, index=True)
    title          = Column(String(500), nullable=False)
    snippet        = Column(Text, nullable=True)
    url            = Column(String(1000), unique=True, nullable=False)
    source_domain  = Column(String(255), nullable=True)
    published_at   = Column(DateTime(timezone=True), nullable=True)
    status         = Column(String(20), default="PENDING")
    # PENDING | WATCH | KEEP | KEEP_URGENT | TRASH | PROCESSED | INACCESSIBLE
    # WATCH      = relevant, contains informative value, does not proceed to Stage 3
    # KEEP       = high importance, queued for Stage 3 with a 5-second delay
    # KEEP_URGENT= extremely critical, bypasses queue straight to Stage 3
    impact_score   = Column(Float, nullable=True)
    category       = Column(String(50), nullable=True)
    # Assigned by AI: "AI_RESEARCH" | "LAYOFF" | "VN_MARKET" | "DEV_TOOLS"
    #                 | "SECURITY" | "BUSINESS" | "OTHER"
    matched_topics = Column(JSON, nullable=True)   # List[str] — matched whitelist topics
