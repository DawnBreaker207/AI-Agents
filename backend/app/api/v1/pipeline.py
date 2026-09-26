import asyncio
import json
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.news import PendingNews
from app.schemas.common import APIResponse
from app.services.pipeline.orchestrator import run_pipeline
from app.services.pipeline.stage3_deep import DeepAnalysisStage

router = APIRouter()
logger = logging.getLogger(__name__)


async def _run_deep_analysis_bg(news_id: int):
    async with AsyncSessionLocal() as db:
        stage = DeepAnalysisStage()
        await stage.run(news_id, db)


async def _run_pipeline_bg():
    await run_pipeline()


async def _translate_titles_bg():
    from app.core.brain import BrainService

    brain = BrainService()
    BATCH_SIZE = 20

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PendingNews)
            .where(PendingNews.status.in_(["KEEP_URGENT", "KEEP", "WATCH", "PENDING"]))
            .order_by(PendingNews.id.desc())
            .limit(200)
        )
        all_news = result.scalars().all()

        def is_mostly_latin(text: str) -> bool:
            latin = sum(1 for c in text if c.isascii() and c.isalpha())
            total = sum(1 for c in text if c.isalpha())
            return total > 0 and (latin / total) > 0.7

        english_news = [n for n in all_news if is_mostly_latin(n.title)]
        logger.info(f"[TranslateTask] Found {len(english_news)} articles with English-like titles.")

        for i in range(0, len(english_news), BATCH_SIZE):
            batch = english_news[i:i + BATCH_SIZE]
            payload = [{"id": n.id, "title": n.title} for n in batch]

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Bạn là dịch giả chuyên nghiệp. Nhiệm vụ: Dịch tiêu đề bài báo công nghệ sang tiếng Việt tự nhiên, chuyên ngành.\n"
                        "Quy tắc:\n"
                        "1. Giữ nguyên tên riêng (tên công ty, người, sản phẩm, tên kỹ thuật như 'GPT-4', 'React', 'AWS').\n"
                        "2. Nếu tiêu đề đã là tiếng Việt, giữ nguyên.\n"
                        "3. Trả về ĐÚNG định dạng JSON: {\"translations\": [{\"id\": 1, \"title_vi\": \"Tiêu đề tiếng Việt\"}]}"
                    )
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ]

            try:
                response = await brain.call_ai_async(messages, model_tier="low", force_json=True)
                parsed = json.loads(response)
                translations = parsed.get("translations", [])

                for t in translations:
                    news_id = t.get("id")
                    title_vi = (t.get("title_vi") or "").strip()
                    if news_id and title_vi:
                        news_item = next((n for n in batch if n.id == news_id), None)
                        if news_item and title_vi != news_item.title:
                            news_item.title = title_vi

                await db.commit()
                logger.info(f"[TranslateTask] Batch {i // BATCH_SIZE + 1}: translated {len(translations)} titles.")
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"[TranslateTask] Batch {i // BATCH_SIZE + 1} error: {e}")

    logger.info("[TranslateTask] Done translating existing titles.")


@router.post("/api/research/{news_id}", status_code=202)
async def trigger_deep_analysis(
    news_id: int,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(_run_deep_analysis_bg, news_id)
    logger.info(f"Deep analysis triggered for news #{news_id}")
    return {"status": "accepted", "message": f"Đang phân tích tin #{news_id}"}


@router.post("/api/pipeline/trigger", status_code=202)
async def trigger_pipeline(background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_pipeline_bg)
    logger.info("Pipeline manual trigger requested.")
    return {"status": "accepted", "message": "Pipeline đang được kích hoạt thu thập thông tin..."}


@router.post("/api/pipeline/translate", status_code=202)
async def translate_existing_titles(background_tasks: BackgroundTasks):
    background_tasks.add_task(_translate_titles_bg)
    logger.info("Batch title translation triggered.")
    return {"status": "accepted", "message": "Đang dịch tiêu đề sang tiếng Việt... Tải lại trang sau vài phút."}
