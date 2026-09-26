from sqlalchemy import Column, Integer, String, Boolean, Float
from app.database import Base

class TopicWhitelist(Base):
    __tablename__ = "topic_whitelist"
    id          = Column(Integer, primary_key=True, index=True)
    topic       = Column(String(200), nullable=False, unique=True)
    # Example: "Java Spring Boot", "Angular", "AI layoff", "Vietnam tech market"
    boost_score = Column(Float, default=1.5)
    # Factor multiplied with impact_score if this topic is detected in the article
    force_keep  = Column(Boolean, default=False)
    # True = always analyze (KEEP) even if impact_score < 8
    is_active   = Column(Boolean, default=True)


class RoleAlias(Base):
    """Từ điển đồng nghĩa vai trò cho Job Search (4.2) — quản lý qua UI."""
    __tablename__ = "role_alias"
    id             = Column(Integer, primary_key=True, index=True)
    canonical_role = Column(String(200), nullable=False)  # VD: "Backend Developer"
    alias          = Column(String(200), nullable=False, unique=True)  # VD: "Server-side Engineer"
    is_active      = Column(Boolean, default=True)
