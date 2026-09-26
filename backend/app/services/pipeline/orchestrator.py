import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.news import PendingNews
from app.services.pipeline.stage1_scout import ScoutStage
from app.services.pipeline.stage2_filter import GatekeeperStage
from app.services.pipeline.stage3_deep import DeepAnalysisStage
from app.core.config import settings

logger = logging.getLogger(__name__)


async def _get_status(news_id: int) -> str:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PendingNews).where(PendingNews.id == news_id))
        news = result.scalar_one_or_none()
        return news.status if news else ""


async def run_pipeline(source_filter: str | None = None):
    logger.info(f"Pipeline starting... (source_filter={source_filter})")

    try:
        async with AsyncSessionLocal() as db:
            await ScoutStage().run(db, source_filter=source_filter)
    except Exception as e:
        logger.error(f"Stage 1 (Scout) failed: {e}", exc_info=True)
        return  # Không chạy tiếp nếu Scout lỗi

    await asyncio.sleep(settings.LLM_CALL_DELAY)

    try:
        async with AsyncSessionLocal() as db:
            all_ids = await GatekeeperStage().run(db)
    except Exception as e:
        logger.error(f"Stage 2 (Gatekeeper) failed: {e}", exc_info=True)
        return

    urgent_ids = []
    normal_ids = []
    for news_id in all_ids:
        status = await _get_status(news_id)
        if status == "KEEP_URGENT":
            urgent_ids.append(news_id)
        else:
            normal_ids.append(news_id)

    for news_id in urgent_ids:
        try:
            async with AsyncSessionLocal() as db:
                await DeepAnalysisStage().run(news_id, db)
        except Exception as e:
            logger.error(f"Stage 3 URGENT error [news_id={news_id}]: {e}")
        await asyncio.sleep(settings.LLM_CALL_DELAY)

    for news_id in normal_ids:
        try:
            async with AsyncSessionLocal() as db:
                await DeepAnalysisStage().run(news_id, db)
        except Exception as e:
            logger.error(f"Stage 3 error [news_id={news_id}]: {e}")
        await asyncio.sleep(settings.STAGE3_DELAY_SECONDS)

    logger.info("Pipeline completed.")


async def run_high_priority_pipeline():
    """Quét dày nhóm nguồn 'high' — Gatekeeper/Stage 3 xử lý PENDING như pipeline chính."""
    await run_pipeline(source_filter="high")


def start_cron_jobs():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline, "interval",
        hours=settings.PIPELINE_INTERVAL_HOURS,
        id="main_pipeline"
    )
    scheduler.add_job(
        run_high_priority_pipeline, "interval",
        minutes=settings.HIGH_PRIORITY_SCAN_MINUTES,
        id="high_priority_scan"
    )
    scheduler.start()
    logger.info(
        f"Scheduler started: pipeline every {settings.PIPELINE_INTERVAL_HOURS}h, "
        f"high-priority scan every {settings.HIGH_PRIORITY_SCAN_MINUTES}m."
    )


async def execute_workflow(topic: str):
    logger.info(f"Manual pipeline triggered with topic: {topic}")
    await run_pipeline()
    return {"status": "success", "msg": "Pipeline completed."}
