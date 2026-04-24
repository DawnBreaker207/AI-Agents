import json
from typing import List

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session, join

from app.core.engine import AgentEngine
from app.models import AgentReportModel
from app.schemas import AgentReport
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["Agent Operations"])
agent_engine = AgentEngine()


@router.get(
    "/health",
    summary="Check agent status")
async def health_check():
    return {"status": "running", "agent": "Maestro-01"}


@router.post(
    "/analyze",
    response_model=AgentReport)
async def analyze_url(
        url: str = Query(...),
        db: Session = Depends(get_db)):
    try:
        raw_answer = agent_engine.run(f"Hãy truy cập URL {url} và phân tích nội dung.")

        if isinstance(raw_answer, str):
            try:
                data = json.loads(raw_answer)
            except:
                data = {
                    "title": "Báo cáo phân tích web",
                    "key_points": [raw_answer],
                    "sentiment": "Chưa xác định",
                    "token_usage_saved": 0
                }
        else:
            data = raw_answer

        report_data = {
            "title": data.get("title", "Không có tiêu đề"),
            "key_points": data.get("key_points", ["Không có nội dung"]),
            "sentiment": data.get("sentiment", "Trung lập"),
            "token_usage_saved": data.get("token_usage_saved", 0)
        }

        db_report = AgentReportModel(
            title=report_data['title'],
            key_points=json.dumps(report_data['key_points']),
            sentiment=report_data['sentiment'],
            token_usage_saved=report_data['token_usage_saved']
        )
        db.add(db_report)
        db.commit()

        return report_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/history",
    response_model=List[AgentReport],
    summary="Take agent action history")
async def get_history(db: Session = Depends(get_db)):
    reports = db.query(AgentReportModel).all()
    results = []
    for r in reports:
        results.append(AgentReport(
            title=r.title,
            key_points=json.loads(r.key_points),
            sentiment=r.sentiment,
            token_usage_saved=r.token_usage_saved
        ))
    return results
