import json
import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.engine import AgentEngine
from app.models.report import ResearchReportModel
from app.schemas.schemas import ResearchReport, ResearchRequest
from database import get_db
from schemas.schemas import clean_sentiment

agent_router = APIRouter()

logger = logging.getLogger(__name__)


@agent_router.get("/health", summary="Kiểm tra trạng thái của agent")
async def health_check():
    return {"status": "running", "agent": "GlobalTechTalentAgent-01"}


@agent_router.post("/research", summary="Thực hiện nghiên cứu chuyên sâu về một chủ đề")
async def research_topic(
        request: ResearchRequest,
        db: Session = Depends(get_db)):
    topic = request.topic
    agent_engine = AgentEngine()

    try:
        user_prompt = f"Hãy nghiên cứu về chủ đề sau: '{topic}'. Tìm các tin tức, bài báo liên quan, và tổng hợp lại thành một báo cáo chi tiết."
        logger.info(f"Starting research for topic: '{topic}'")
        report_data = await agent_engine.run(user_prompt)

        if not report_data or not report_data.get("summary") or len(report_data.get("summary")) < 10:
            logger.warning(f"Research failed or returned empty data for topic: {topic}")
            raise HTTPException(
                status_code=422,
                detail="Agent không tìm thấy thông tin hữu ích cho chủ đề này. Dữ liệu không được lưu."
            )

        raw_sentiment = report_data.get("sentiment")
        valid_sentiment = clean_sentiment(raw_sentiment)

        current_time = datetime.now(timezone.utc)
        research_report = ResearchReport(
            title=f"Báo cáo nghiên cứu về: {topic}",
            summary=report_data.get("summary"),
            key_points=report_data.get("key_points", []),
            sentiment=valid_sentiment,
            sources=report_data.get("sources", []),
            categories=report_data.get("categories", []),
            regions=report_data.get("regions", []),
            created_at=current_time
        )

        db_report = ResearchReportModel(
            title=research_report.title,
            summary=research_report.summary,
            key_points=json.dumps(research_report.key_points),
            sentiment=research_report.sentiment.value,
            sources=json.dumps(research_report.sources),
            categories=json.dumps(research_report.categories),
            regions=json.dumps(research_report.regions),
            created_at=research_report.created_at
        )

        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        research_report.id = db_report.id
        return research_report
    except Exception as e:
        logger.error(f"Error during research for topic '{topic}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi trong quá trình nghiên cứu: {str(e)}")


@agent_router.get("/history", response_model=List[ResearchReport], summary="Lấy lịch sử các báo cáo nghiên cứu")
async def get_history(db: Session = Depends(get_db)):
    reports = db.query(ResearchReportModel).order_by(ResearchReportModel.id.desc()).all()
    results = []
    for r in reports:

        def parse_json_column(data):
            if not data:
                return []
            if isinstance(data, list):  # Trường hợp key_points đã là list
                return data
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return [data]

        report_data = {
            "id": r.id,
            "title": r.title,
            "summary": r.summary,
            "sentiment": r.sentiment,
            "created_at": r.created_at,
            "key_points": r.key_points if isinstance(r.key_points, list) else parse_json_column(r.key_points),
            "sources": parse_json_column(r.sources),
            "categories": parse_json_column(r.categories),
            "regions": parse_json_column(r.regions),
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

    def parse_json_column(data):
        if not data:
            return []
        if isinstance(data, list):
            return data
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return [data]

    report_data = {
        "id": r.id,
        "title": r.title,
        "summary": r.summary,
        "sentiment": r.sentiment,
        "created_at": r.created_at,
        "key_points": r.key_points if isinstance(r.key_points, list) else parse_json_column(r.key_points),
        "sources": parse_json_column(r.sources),
        "categories": parse_json_column(r.categories),
        "regions": parse_json_column(r.regions),
    }

    return ResearchReport.model_validate(report_data)
