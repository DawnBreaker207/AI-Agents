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
        results.append(ResearchReport.model_validate(r, update={
            "key_points": json.loads(r.key_points),
            "sources": json.loads(r.sources),
            "categories": json.loads(r.categories),
            "regions": json.loads(r.regions)
        }))
    return results
