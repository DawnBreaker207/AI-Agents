from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class JobWatch(Base):
    """Bảng lưu các vị trí việc làm mà người dùng quan tâm / theo dõi."""
    __tablename__ = "job_watches"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String(200), nullable=False)
    level = Column(String(50), default="Tất cả")
    location_type = Column(String(20), default="domestic")
    city = Column(String(100), default="Tất cả")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "level": self.level,
            "location_type": self.location_type,
            "city": self.city,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
