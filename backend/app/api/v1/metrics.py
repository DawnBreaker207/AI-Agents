import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.news import PendingNews
from app.schemas.common import APIResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/metrics", summary="Get feed metrics overview")
async def get_feed_metrics(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(PendingNews.id)))
    total_today = total_result.scalar() or 0

    statuses = ["KEEP_URGENT", "KEEP", "WATCH", "TRASH", "PROCESSED"]
    counts = {}
    for status in statuses:
        res = await db.execute(select(func.count(PendingNews.id)).where(PendingNews.status == status))
        counts[status] = res.scalar() or 0

    return APIResponse(
        message="Số liệu tổng quan của tin tức",
        data={
            "total_today": total_today,
            "keep_urgent": counts["KEEP_URGENT"],
            "keep": counts["KEEP"],
            "watch": counts["WATCH"],
            "trash": counts["TRASH"],
            "processed": counts["PROCESSED"],
            "last_run_at": datetime.now().isoformat() + "Z"
        }
    )
