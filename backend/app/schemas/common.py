from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
