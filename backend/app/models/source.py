from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from app.database import Base

class SourceList(Base):
    __tablename__ = "source_list"
    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(255), nullable=False)
    url                 = Column(String(500), nullable=False, unique=True)
    type                = Column(String(20), default="RSS")        # RSS or SCRAPE feed types
    is_active           = Column(Boolean, default=True)
    priority_weight     = Column(Float, default=1.0)
    scan_priority       = Column(String(10), default="normal")  # high | normal
    consecutive_fails   = Column(Integer, default=0)               # Số lần chạy liên tiếp thất bại
    last_error          = Column(Text, default="")                  # Lỗi gần nhất
    disabled_at         = Column(DateTime, nullable=True)           # Thời điểm bị auto-disable
