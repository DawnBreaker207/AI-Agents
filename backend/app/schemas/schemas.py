from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field, ConfigDict


class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề cần nghiên cứu (VD: Thị trường AI Việt Nam)")
    force_refresh: Optional[bool] = False

class ChatRequest(BaseModel):
    prompt: str
    category: Optional[str] = "all"

class ResearchReport(BaseModel):
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


# --- RESPONSE SCHEMAS ---
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

# --- INTERMEDIATE SCHEMAS (Cho Stage 2) ---
class SignalSchema(BaseModel):
    title: str
    keywords: List[str]
    priority_score: int
    url: str