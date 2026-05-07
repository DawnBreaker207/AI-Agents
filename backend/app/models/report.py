from sqlalchemy import Column, Integer, Float, Text, String, DateTime, JSON
from sqlalchemy.sql import func

from app.database import Base


class ResearchReportModel(Base):
    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True, index=True)

    # Dữ liệu từ Stage 2 & 3
    title = Column(String(255), nullable=False)
    impact_score = Column(Float, default=1)  # Điểm ảnh hưởng 1-10
    tags = Column(JSON, nullable=True)  # Mảng từ khóa [Java, AI...]

    # Dữ liệu từ Stage 4 (Bài viết hoàn chỉnh)
    content = Column(Text, nullable=False)

    raw_analysis = Column(JSON, nullable=True)

    # Meta data (Nguồn gốc)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
