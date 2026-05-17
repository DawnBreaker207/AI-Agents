import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.engine import ChatEngine
from app.core.maestro import MaestroOrchestrator
from app.core.utils import parse_json_column
from app.database import get_db
from app.models.category import TopicWhitelist
from app.models.news import PendingNews
from app.models.report import ResearchReport
from app.models.source import SourceList
from app.schemas.schemas import (
    ChatRequest,
    ResearchReport as ResearchReportSchema,
    APIResponse,
    ResearchRequest
)
from app.stages.stage3_deep import DeepAnalysisStage

api_router = APIRouter()
logger = logging.getLogger(__name__)


@api_router.get("/health", summary="Kiểm tra trạng thái của agent")
async def health_check():
    return APIResponse(
        message="Hệ thống đang hoạt động ổn định.",
        data={"status": "running", "agent": "GlobalTechTalentAgent-01"}
    )


@api_router.post("/research", summary="Kích hoạt hệ thống TSI thực hiện nghiên cứu")
async def research_topic(request: ResearchRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    orchestrator = MaestroOrchestrator()
    background_tasks.add_task(orchestrator.execute_workflow, request.topic, db)

    return APIResponse(
        message=f"Hệ thống đang điều tra chiến lược: {request.topic}. Kết quả sẽ tự động lưu vào Dashboard.",
        data={"status": "processing", "agent": "TechScout-01", "topic": request.topic}
    )


@api_router.post("/chat", summary="Hỏi đáp với Chuyên gia AI dựa trên dữ liệu báo cáo")
async def chat_with_analyst(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    query = select(ResearchReport)
    if request.category and request.category != "all":
        pass

    query = query.order_by(ResearchReport.created_at.desc()).limit(5)
    result = await db.execute(query)
    context_reports = result.scalars().all()

    engine = ChatEngine()
    answer = await engine.run_analyst(request.prompt, context_reports)

    return APIResponse(
        message="Phản hồi từ AI Analyst",
        data={"answer": answer}
    )


@api_router.get("/history", summary="Lấy lịch sử các báo cáo nghiên cứu")
async def get_history(category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(ResearchReport)
    result = await db.execute(query.order_by(ResearchReport.id.desc()))
    reports = result.scalars().all()

    results = []
    for r in reports:
        analysis = r.raw_analysis if r.raw_analysis else {}
        report_data = {
            "id": r.id,
            "title": r.title,
            "topic": getattr(r, "topic", r.title),
            "summary": r.executive_summary or "",
            "impact_score": float(r.impact_score),
            "created_at": r.created_at,
            "last_updated": r.created_at,
            "sentiment": r.sentiment or "Trung tính",
            "categories": parse_json_column(r.tags),
            "regions": ["Việt Nam"],
            "sources": [r.original_source] if r.original_source else [],
            "tech_trends": analysis.get("tech_trends", []),
            "employment_status": analysis.get("employment_status", {}),
            "job_details": analysis.get("job_details", {}),
            "research_articles": []
        }
        results.append(ResearchReportSchema.model_validate(report_data))
    
    return APIResponse(
        message=f"Tìm thấy {len(results)} báo cáo.",
        data=results
    )


@api_router.get("/report/{report_id}", summary="Lấy chi tiết một báo cáo nghiên cứu")
async def get_report_by_id(report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchReport).where(ResearchReport.id == report_id))
    r = result.scalar_one_or_none()

    if not r:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy báo cáo nghiên cứu với ID: {report_id}"
        )
    analysis = r.raw_analysis if r.raw_analysis else {}
    report_data = {
        "id": r.id,
        "title": r.title,
        "topic": getattr(r, "topic", r.title),
        "summary": r.executive_summary or "",
        "impact_score": float(r.impact_score),
        "created_at": r.created_at,
        "last_updated": r.created_at,
        "sentiment": r.sentiment or "Trung tính",
        "categories": parse_json_column(r.tags),
        "regions": ["Việt Nam"],
        "sources": [r.original_source] if r.original_source else [],
        "tech_trends": analysis.get("tech_trends", []),
        "employment_status": analysis.get("employment_status", {}),
        "job_details": analysis.get("job_details", {}),
        "research_articles": []
    }

    return APIResponse(
        message="Chi tiết báo cáo nghiên cứu.",
        data=ResearchReportSchema.model_validate(report_data)
    )


from fastapi.responses import StreamingResponse
from app.database import AsyncSessionLocal

@api_router.get("/api/news/stream")
async def stream_news():
    """SSE Endpoint for Realtime News Feed Updates"""
    async def event_generator():
        last_id = 0
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(PendingNews.id).order_by(PendingNews.id.desc()).limit(1))
            last_id = result.scalar_one_or_none() or 0
            
        while True:
            await asyncio.sleep(3)
            try:
                async with AsyncSessionLocal() as db:
                    new_items_result = await db.execute(
                        select(PendingNews.id).where(PendingNews.id > last_id).order_by(PendingNews.id.desc())
                    )
                    new_ids = new_items_result.scalars().all()
                    if new_ids:
                        last_id = new_ids[0]
                        yield f"data: {json.dumps({'type': 'new_news'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'ping'})}\n\n"
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"SSE Error: {e}")
                await asyncio.sleep(5)
                
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@api_router.get("/api/news/pending")
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


@api_router.get("/api/news/keep")
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


@api_router.get("/api/news/keep_urgent")
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


@api_router.get("/api/news/watch")
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


@api_router.get("/api/news/inaccessible")
async def get_inaccessible_news(
        page: int = 1, size: int = 20,
        db: AsyncSession = Depends(get_db)
):
    """
    Danh sách tin Stage 3 không đọc được nội dung.
    Dùng để monitor chất lượng nguồn RSS và retry thủ công nếu cần.
    """
    offset = (page - 1) * size
    result = await db.execute(
        select(PendingNews)
        .where(PendingNews.status == "INACCESSIBLE")
        .order_by(PendingNews.published_at.desc())
        .offset(offset).limit(size)
    )
    return result.scalars().all()


@api_router.post("/api/news/{news_id}/promote", status_code=202)
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
    background_tasks.add_task(DeepAnalysisStage().run, news_id, db)
    return {"status": "promoted", "news_id": news_id,
            "message": f"Tin #{news_id} đang được phân tích sâu."}


@api_router.post("/api/news/{news_id}/retry", status_code=202)
async def retry_inaccessible(
        news_id: int,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    """Retry phân tích cho tin INACCESSIBLE — reset về KEEP và chạy lại Stage 3."""
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
    background_tasks.add_task(DeepAnalysisStage().run, news_id, db)
    return {"status": "retrying", "news_id": news_id,
            "message": f"Tin #{news_id} sẽ được phân tích lại."}


from app.worker.scheduler import run_pipeline
import asyncio

@api_router.post("/api/pipeline/trigger", status_code=202)
async def trigger_pipeline(background_tasks: BackgroundTasks):
    """
    Kích hoạt pipeline thủ công (Scout -> Gatekeeper -> Deep Analysis).
    Chạy ngầm (background task) để không chặn request.
    """
    background_tasks.add_task(run_pipeline)
    return {"status": "accepted", "message": "Pipeline đang được kích hoạt thu thập thông tin..."}


async def _batch_translate_titles():
    """Background task: dịch hàng loạt tiêu đề tiếng Anh sang tiếng Việt."""
    from app.core.brain import BrainService

    brain = BrainService()
    BATCH_SIZE = 20

    async with AsyncSessionLocal() as db:
        # Lấy những bài có tiêu đề chứa ký tự Latin (khả năng cao là tiếng Anh)
        result = await db.execute(
            select(PendingNews)
            .where(PendingNews.status.in_(["KEEP_URGENT", "KEEP", "WATCH", "PENDING"]))
            .order_by(PendingNews.id.desc())
            .limit(200)
        )
        all_news = result.scalars().all()

        # Lọc những bài tiêu đề có vẻ chưa phải tiếng Việt (chủ yếu Latin)
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
                await asyncio.sleep(1)  # rate limit

            except Exception as e:
                logger.error(f"[TranslateTask] Batch {i // BATCH_SIZE + 1} error: {e}")

    logger.info("[TranslateTask] Done translating existing titles.")


@api_router.post("/api/pipeline/translate", status_code=202)
async def translate_existing_titles(background_tasks: BackgroundTasks):
    """
    Dịch hàng loạt tiêu đề tiếng Anh trong DB sang tiếng Việt.
    Chạy ngầm để không chặn request.
    """
    background_tasks.add_task(_batch_translate_titles)
    return {"status": "accepted", "message": "Đang dịch tiêu đề sang tiếng Việt... Tải lại trang sau vài phút."}

@api_router.post("/api/research/{news_id}", status_code=202)
async def trigger_deep_analysis(
        news_id: int,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    background_tasks.add_task(DeepAnalysisStage().run, news_id, db)
    return {"status": "accepted", "message": f"Đang phân tích tin #{news_id}"}


def _sanitize_report_field(value) -> str | None:
    """
    Convert DB-stored field to clean human-readable text.
    Handles: plain string, JSON-encoded string (old data), list[dict], dict.
    """
    import json as _json
    if not value:
        return None

    # Trường hợp đã là string sạch
    if isinstance(value, str):
        stripped = value.strip()
        # Thử parse nếu là JSON string (dữ liệu cũ)
        if stripped.startswith(("[", "{")):
            try:
                value = _json.loads(stripped)
            except Exception:
                # Không parse được -> trả nguyên
                return stripped
        else:
            return stripped

    # Từ đây value có thể là list hoặc dict
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                # Format các kiểu list[dict] phổ biến
                trend   = item.get("trend") or item.get("name") or item.get("title") or ""
                desc    = item.get("description") or item.get("update") or item.get("details") or ""
                if trend and desc:
                    lines.append(f"• **{trend}**: {desc}")
                elif trend:
                    lines.append(f"• {trend}")
                elif desc:
                    lines.append(f"• {desc}")
                else:
                    lines.append("• " + ", ".join(f"{k}: {v}" for k, v in item.items()))
            else:
                lines.append(f"• {item}")
        return "\n".join(lines) or None

    if isinstance(value, dict):
        LABEL_MAP = {
            "status": "Trạng thái thị trường",
            "market": "Thị trường",
            "demand": "Nhu cầu tuyển dụng",
            "details": "Chi tiết",
        }
        parts = []
        for k, v in value.items():
            label = LABEL_MAP.get(k, k.capitalize())
            parts.append(f"**{label}:** {v}")
        return "\n".join(parts) or None

    return str(value) or None


@api_router.get("/api/reports/strategic")
async def get_strategic_reports(
        page: int = 1, size: int = 20,
        db: AsyncSession = Depends(get_db)
):
    """
    Danh sách báo cáo chiến lược.
    Response bao gồm source_citations để frontend hiển thị link dẫn chứng.
    """
    offset = (page - 1) * size
    result = await db.execute(
        select(ResearchReport)
        .order_by(ResearchReport.created_at.desc())
        .offset(offset).limit(size)
    )
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "original_source": r.original_source,
            "executive_summary": r.executive_summary,
            "technical_deep_dive": _sanitize_report_field(r.technical_deep_dive),
            "vietnam_market_impact": _sanitize_report_field(r.vietnam_market_impact),
            "strategic_action_items": r.strategic_action_items or [],
            "impact_score": r.impact_score,
            "sentiment": r.sentiment,
            "tags": r.tags or [],
            "created_at": r.created_at,
            "source_citations": (
                    r.source_citations
                    or ([r.original_source] if r.original_source else [])
            ),
        }
        for r in reports
    ]


@api_router.get("/api/reports/{report_id}")
async def get_report_detail(
        report_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Chi tiết 1 báo cáo, bao gồm source_citations và metadata fetch.
    Response example:
    {
      "id": 42,
      "title": "...",
      "original_source": "https://techcrunch.com/...",
      "source_citations": ["https://techcrunch.com/...", "https://reuters.com/..."],
      "citation_count": 2,
      "fetch_method": "jina_reader",
      "content_length_fetched": 4823
    }
    """
    result = await db.execute(
        select(ResearchReport).where(ResearchReport.id == report_id)
    )
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo.")

    pending_news = None
    if r.pending_news_id:
        news_result = await db.execute(
            select(PendingNews).where(PendingNews.id == r.pending_news_id)
        )
        pending_news = news_result.scalar_one_or_none()

    citations = (
            r.source_citations
            or ([r.original_source] if r.original_source else [])
    )

    return {
        "id": r.id,
        "title": r.title,
        "original_source": r.original_source,
        "executive_summary": r.executive_summary,
        "technical_deep_dive": _sanitize_report_field(r.technical_deep_dive),
        "vietnam_market_impact": _sanitize_report_field(r.vietnam_market_impact),
        "strategic_action_items": r.strategic_action_items or [],
        "impact_score": r.impact_score,
        "sentiment": r.sentiment,
        "tags": r.tags or [],
        "created_at": r.created_at,
        "source_citations": citations,
        "citation_count": len(citations),
        "fetch_method": (r.raw_analysis or {}).get("fetch_method", "unknown"),
        "content_length_fetched": (r.raw_analysis or {}).get("content_length_fetched", 0),
        "source_news": {
            "id": pending_news.id if pending_news else None,
            "source_domain": pending_news.source_domain if pending_news else None,
            "published_at": pending_news.published_at if pending_news else None,
            "category": pending_news.category if pending_news else None,
        } if pending_news else None,
    }


@api_router.get("/api/sources")
async def get_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SourceList).order_by(SourceList.id.desc()))
    return result.scalars().all()


@api_router.put("/api/sources/{source_id}/toggle")
async def toggle_source(
        source_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SourceList).where(SourceList.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Không tìm thấy nguồn.")
    source.is_active = not source.is_active
    await db.commit()
    return {"id": source_id, "is_active": source.is_active}


@api_router.get("/api/whitelist")
async def get_whitelist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TopicWhitelist))
    return result.scalars().all()


@api_router.post("/api/whitelist", status_code=201)
async def add_whitelist_topic(
        topic: str, boost_score: float = 1.5, force_keep: bool = False,
        db: AsyncSession = Depends(get_db)
):
    db.add(TopicWhitelist(topic=topic, boost_score=boost_score, force_keep=force_keep))
    await db.commit()
    return {"status": "created", "topic": topic}


@api_router.delete("/api/whitelist/{topic_id}")
async def delete_whitelist_topic(
        topic_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(TopicWhitelist).where(TopicWhitelist.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Không tìm thấy topic.")
    await db.delete(topic)
    await db.commit()
    return {"status": "deleted"}


@api_router.get("/api/metrics", summary="Lấy số liệu tổng quan của feed tin tức")
async def get_feed_metrics(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    
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
