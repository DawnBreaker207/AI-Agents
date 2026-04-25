import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.models.report import ResearchReportModel
from app.schemas.schemas import ResearchReport, ResearchRequest
from core.maestro import MaestroOrchestrator
from database import get_db

agent_router = APIRouter()

logger = logging.getLogger(__name__)


@agent_router.get("/health", summary="Kiểm tra trạng thái của agent")
async def health_check():
    return {"status": "running", "agent": "GlobalTechTalentAgent-01"}


@agent_router.post("/auto_sync")
async def daily_market_scan(
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)):
    orchestrator = MaestroOrchestrator()
    hot_topics = ["AI Trends 2025", "IT Job Market Vietnam", "Semiconductor Industry"]

    for topic in hot_topics:
        background_tasks.add_task(orchestrator.execute_workflow, topic, db, True)

    return {"message": "Maestro đang quét thị trường ngầm..."}


@agent_router.post("/research", summary="Thực hiện nghiên cứu chuyên sâu về một chủ đề")
async def research_topic(
        request: ResearchRequest,
        db: Session = Depends(get_db)):
    topic = request.topic
    orchestrator = MaestroOrchestrator()
    try:
        report = await orchestrator.execute_workflow(
            topic=request.topic,
            db=db,
            force_refresh=request.force_refresh
        )
        return report
    except Exception as e:
        logger.error(f"Error during research for topic '{topic}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi trong quá trình nghiên cứu: {str(e)}")


@agent_router.get("/history", response_model=List[ResearchReport], summary="Lấy lịch sử các báo cáo nghiên cứu")
async def get_history(db: Session = Depends(get_db)):
    reports = db.query(ResearchReportModel).order_by(ResearchReportModel.id.desc()).all()
    results = []
    for r in reports:
        report_data = {
            "id": r.id,
            "topic": getattr(r, "topic", r.title),
            "title": r.title,
            "summary": r.summary,
            "sentiment": r.sentiment,
            "impact_score": getattr(r, "impact_score", 0.0),
            "created_at": r.created_at,
            "categories": parse_json_column(r.categories),
            "regions": parse_json_column(r.regions),
            "sources": parse_json_column(r.sources),
            "last_updated": str(r.created_at),

            "tech_trends": parse_json_column(getattr(r, "tech_trends", []), []),
            "employment_status": parse_json_column(getattr(r, "employment_status", {}), {}),
            "job_details": parse_json_column(getattr(r, "job_details", {}), {}),
            "research_articles": parse_json_column(getattr(r, "research_articles", []), [])
        }
        results.append(ResearchReport.model_validate(report_data))
    return results


@agent_router.get("/report/{report_id}", response_model=ResearchReport, summary="Lấy chi tiết một báo cáo nghiên cứu")
async def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    r = db.query(ResearchReportModel).filter(ResearchReportModel.id == report_id).first()

    if not r:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy báo cáo nghiên cứu với ID: {report_id}"
        )

    report_data = {
        "id": r.id,
        "topic": getattr(r, "topic", r.title),
        "title": r.title,
        "summary": r.summary,
        "sentiment": r.sentiment,
        "impact_score": getattr(r, "impact_score", 0.0),
        "created_at": r.created_at,
        "categories": parse_json_column(r.categories),
        "regions": parse_json_column(r.regions),
        "sources": parse_json_column(r.sources),
        "last_updated": str(r.created_at),

        "tech_trends": parse_json_column(getattr(r, "tech_trends", []), []),
        "employment_status": parse_json_column(getattr(r, "employment_status", {}), {}),
        "job_details": parse_json_column(getattr(r, "job_details", {}), {}),
        "research_articles": parse_json_column(getattr(r, "research_articles", []), [])
    }

    return ResearchReport.model_validate(report_data)


def parse_json_column(data, default_value=None):
    if default_value is None:
        default_value = []
    if not data:
        return default_value
    if isinstance(data, (list, dict)):
        return data
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default_value
