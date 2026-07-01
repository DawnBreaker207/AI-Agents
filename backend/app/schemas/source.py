from pydantic import BaseModel, ConfigDict


class SourceListSchema(BaseModel):
    id: int
    name: str
    url: str
    type: str
    is_active: bool
    priority_weight: float

    model_config = ConfigDict(from_attributes=True)
