from pydantic import BaseModel
from typing import List


class AgentReport(BaseModel):
    title: str
    key_points: List[str]
    sentiment: str
    token_usage_saved: int

    class Config:
        from_attributes = True
