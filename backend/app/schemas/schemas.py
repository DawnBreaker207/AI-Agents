from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
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
    id: Optional[int] = Field(None, description="ID duy nhất của báo cáo, thường được tạo bởi cơ sở dữ liệu.")
    title: str = Field(..., description="Tiêu đề của báo cáo nghiên cứu.")
    summary: Optional[str] = Field(None, description="Tóm tắt nội dung chính của báo cáo.")
    key_points: List[str] = Field(default_factory=list, description="Các điểm chính được rút ra từ báo cáo.")
    sentiment: SentimentEnum = Field(SentimentEnum.UNDEFINED, description="Cảm xúc tổng thể của báo cáo.")
    sources: List[str] = Field(default_factory=list, description="Danh sách các nguồn tham khảo được sử dụng.")
    created_at: datetime = Field(..., description="Thời điểm báo cáo được tạo (UTC).")
    categories: List[str] = Field(
        default_factory=list,
        description="Các danh mục chính của báo cáo (ví dụ: 'Công nghệ', 'Thị trường', 'Tuyển dụng')."
    )
    regions: List[str] = Field(
        default_factory=list,
        description="Các khu vực địa lý mà báo cáo đề cập (ví dụ: 'Toàn cầu', 'Việt Nam', 'Châu Á')."
    )

    model_config = ConfigDict(from_attributes=True)


class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề cần nghiên cứu")
