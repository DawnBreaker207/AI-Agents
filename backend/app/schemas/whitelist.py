from pydantic import BaseModel, ConfigDict


class TopicWhitelistSchema(BaseModel):
    id: int
    topic: str
    boost_score: float
    force_keep: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
