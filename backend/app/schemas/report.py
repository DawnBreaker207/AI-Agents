from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, ConfigDict


class ResearchReportSchema(BaseModel):
    id: Optional[int] = None
    title: str
    topic: Optional[str] = None
    summary: Optional[str] = None
    impact_score: float = 0.0

    tech_trends: Optional[List[Dict]] = []
    employment_status: Optional[Dict] = {}
    job_details: Optional[Dict] = {}
    research_articles: Optional[List[Dict]] = []

    categories: Optional[List[str]] = []
    regions: Optional[List[str]] = []
    sentiment: Optional[str] = "Trung tính"
    sources: List[str] = []
    created_at: datetime
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    id: int
    title: str
    content: str
    impact_score: int
    tags: Optional[List[str]] = []
    source_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
