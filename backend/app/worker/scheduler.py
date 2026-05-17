import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import PendingNews
from app.stages.stage1_scout import ScoutStage
from app.stages.stage2_filter import GatekeeperStage
from app.stages.stage3_deep import DeepAnalysisStage

logger = logging.getLogger(__name__)


async def _get_status(news_id: int) -> str:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PendingNews).where(PendingNews.id == news_id))
        news = result.scalar_one_or_none()
        return news.status if news else ""


async def run_pipeline():
    """Coordinate Stage 1 and Stage 2 automatic schedules, then branch Stage 3 jobs."""
    logger.info("Pipeline starting...")

    # Stage 1: Fetch and normalize active feeds
    async with AsyncSessionLocal() as db:
        await ScoutStage().run(db)

    # Stage 2: Filter and score feeds using low-tier model
    async with AsyncSessionLocal() as db:
        all_ids = await GatekeeperStage().run(db)

    urgent_ids = []
    normal_ids = []
    for news_id in all_ids:
        status = await _get_status(news_id)
        if status == "KEEP_URGENT":
            urgent_ids.append(news_id)
        else:
            normal_ids.append(news_id)

    # KEEP_URGENT: Process deep analysis immediately with no delay
    for news_id in urgent_ids:
        try:
            async with AsyncSessionLocal() as db:
                await DeepAnalysisStage().run(news_id, db)
        except Exception as e:
            logger.error(f"Stage 3 URGENT error [news_id={news_id}]: {e}")

    # KEEP: Process sequentially with a 5-second delay between items to avoid rate limits
    for news_id in normal_ids:
        try:
            async with AsyncSessionLocal() as db:
                await DeepAnalysisStage().run(news_id, db)
        except Exception as e:
            logger.error(f"Stage 3 error [news_id={news_id}]: {e}")
        await asyncio.sleep(5)

    logger.info("Pipeline completed.")


def start_cron_jobs():
    """Initialize and start the background scheduler running the pipeline every 4 hours."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_pipeline, "interval", hours=4, id="main_pipeline")
    scheduler.start()
    logger.info("Scheduler started: pipeline running every 4 hours.")
