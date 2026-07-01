from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề cần nghiên cứu")
    force_refresh: Optional[bool] = False


class ChatRequest(BaseModel):
    prompt: str
    category: Optional[str] = "all"


class APIResponse(BaseModel):
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
