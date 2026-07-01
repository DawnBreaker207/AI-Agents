import logging

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.models.news import PendingNews
from app.services.pipeline.stage3_deep import DeepAnalysisStage

router = APIRouter(prefix="/api/news")
logger = logging.getLogger(__name__)


async def _run_deep_analysis(news_id: int):
    async with AsyncSessionLocal() as db:
        stage = DeepAnalysisStage()
        await stage.run(news_id, db)


@router.get("/stream")
async def stream_news():
    from app.core.events import news_broadcaster
    return StreamingResponse(news_broadcaster.subscribe(), media_type="text/event-stream")


@router.get("/pending")
async def get_pending_news(
    page: int = 1, size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * size
    result = await db.execute(
        select(PendingNews)
        .where(PendingNews.status == "PENDING")
        .offset(offset).limit(size)
    )
    return result.scalars().all()


@router.get("/keep")
async def get_keep_news(
    page: int = 1, size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * size
    result = await db.execute(
        select(PendingNews)
        .where(PendingNews.status == "KEEP")
        .order_by(PendingNews.impact_score.desc())
        .offset(offset).limit(size)
    )
    return result.scalars().all()


@router.get("/keep_urgent")
async def get_keep_urgent_news(
    page: int = 1, size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * size
    result = await db.execute(
        select(PendingNews)
        .where(PendingNews.status == "KEEP_URGENT")
        .order_by(PendingNews.impact_score.desc())
        .offset(offset).limit(size)
    )
    return result.scalars().all()


@router.get("/watch")
async def get_watch_news(
    page: int = 1, size: int = 20,
    category: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(PendingNews)
        .where(PendingNews.status == "WATCH")
        .order_by(PendingNews.impact_score.desc())
    )
    if category:
        query = query.where(PendingNews.category == category)
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/inaccessible")
async def get_inaccessible_news(
    page: int = 1, size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * size
    result = await db.execute(
        select(PendingNews)
        .where(PendingNews.status == "INACCESSIBLE")
        .order_by(PendingNews.published_at.desc())
        .offset(offset).limit(size)
    )
    return result.scalars().all()


@router.post("/{news_id}/promote", status_code=202)
async def promote_to_keep(
    news_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(PendingNews).where(PendingNews.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin.")
    if news.status not in ("WATCH", "TRASH"):
        raise HTTPException(
            status_code=400,
            detail=f"Tin đang ở status {news.status}, không thể promote."
        )
    news.status = "KEEP"
    await db.commit()
    background_tasks.add_task(_run_deep_analysis, news_id)
    logger.info(f"Promoted news #{news_id} to KEEP, queuing deep analysis.")
    return {"status": "promoted", "news_id": news_id,
            "message": f"Tin #{news_id} đang được phân tích sâu."}


@router.post("/{news_id}/retry", status_code=202)
async def retry_inaccessible(
    news_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(PendingNews).where(PendingNews.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin.")
    if news.status != "INACCESSIBLE":
        raise HTTPException(
            status_code=400,
            detail=f"Tin đang ở status '{news.status}', chỉ retry được INACCESSIBLE."
        )
    news.status = "KEEP"
    await db.commit()
    background_tasks.add_task(_run_deep_analysis, news_id)
    logger.info(f"Retrying inaccessible news #{news_id}, queuing deep analysis.")
    return {"status": "retrying", "news_id": news_id,
            "message": f"Tin #{news_id} sẽ được phân tích lại."}
