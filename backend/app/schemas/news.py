from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict


class PendingNewsSchema(BaseModel):
    id: int
    title: str
    snippet: Optional[str] = None
    url: str
    source_domain: Optional[str] = None
    published_at: Optional[datetime] = None
    status: str
    impact_score: Optional[float] = None
    category: Optional[str] = None
    matched_topics: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
