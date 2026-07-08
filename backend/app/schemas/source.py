from pydantic import BaseModel, ConfigDict


class SourceListSchema(BaseModel):
    id: int
    name: str
    url: str
    type: str
    is_active: bool
    priority_weight: float
    consecutive_fails: int = 0
    last_error: str = ""
    disabled_at: str | None = None

    model_config = ConfigDict(from_attributes=True)
