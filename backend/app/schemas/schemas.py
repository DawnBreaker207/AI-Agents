from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime, timezone
from enum import Enum


class SentimentEnum(str, Enum):
    POSITIVE = "Tích cực"
    NEGATIVE = "Tiêu cực"
    NEUTRAL = "Trung tính"
    UNDEFINED = "Không xác định"


def clean_sentiment(raw_val: str) -> SentimentEnum:
    if not raw_val:
        return SentimentEnum.UNDEFINED

    mapping = {
        "Trung lập": SentimentEnum.NEUTRAL,
        "Trung tính": SentimentEnum.NEUTRAL,
        "Neutral": SentimentEnum.NEUTRAL,
        "Tích cực": SentimentEnum.POSITIVE,
        "Positive": SentimentEnum.POSITIVE,
        "Tiêu cực": SentimentEnum.NEGATIVE,
        "Negative": SentimentEnum.NEGATIVE
    }
    return mapping.get(raw_val.strip(), SentimentEnum.UNDEFINED)


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


class ResearchRequest(BaseModel):
    topic: str
    force_refresh: bool = False


class SoftwareReportSchema(BaseModel):
    summary: str
    impact_score: float
    categories: List[str]
    regions: List[str]
    tech_trends: List[Dict]
    employment_status: Dict
    job_details: Dict
    research_articles: List[Dict]
    sentiment: str
    sources: List[str]


class ChatRequest(BaseModel):
    prompt: str
    category: Optional[str] = "all"
