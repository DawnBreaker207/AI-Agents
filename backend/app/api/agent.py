import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.models.report import ResearchReportModel
from app.schemas.schemas import ResearchReport, ResearchRequest
from core.engine import AgentEngine
from core.maestro import MaestroOrchestrator
from database import get_db
from schemas.schemas import ChatRequest

agent_router = APIRouter()

logger = logging.getLogger(__name__)


@agent_router.get("/health", summary="Kiểm tra trạng thái của agent")
async def health_check():
    return {"status": "running", "agent": "GlobalTechTalentAgent-01"}


@agent_router.get("/signals")
async def get_latest_signals(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    #
    last_report = db.query(ResearchReportModel).order_by(ResearchReportModel.last_updated.desc()).first()
    should_refresh = True
    if last_report and last_report.last_updated:
        last_updated = last_report.last_updated.replace(
            tzinfo=timezone.utc) if last_report.last_updated.tzinfo is None else last_report.last_updated
        if datetime.now(timezone.utc) - last_updated < timedelta(hours=1):
            should_refresh = False

    if should_refresh:
        orchestrator = MaestroOrchestrator()
        STRATEGIC_TOPICS = [
            "Xu hướng sa thải và tuyển dụng ngành IT Việt Nam 2025",
            "Mức lương lập trình viên AI và Software Engineer mới nhất",
            "Báo cáo công nghệ mới nhất từ Gartner và GitHub 2025"
        ]
        for topic in STRATEGIC_TOPICS:
            background_tasks.add_task(orchestrator.execute_workflow, topic, db, False)

    #
    reports = db.query(ResearchReportModel).order_by(ResearchReportModel.last_updated.desc()).limit(20).all()

    #
    streams = {
        "news": [],
        "jobs": [],
        "academic": [],
        "trends": []
    }

    for r in reports:
        if r.sentiment and r.sentiment != "Không xác định":
            streams["news"].append({
                "id": r.id, "title": r.title, "content": r.summary,
                "badge": r.sentiment, "time": r.last_updated, "type": "news"
            })

        job_details = parse_json_column(r.job_details, {})
        emp_status = parse_json_column(r.employment_status, {})
        if job_details.get("salary"):
            streams["jobs"].append({
                "id": r.id,
                "title": f"Lương: {job_details['salary']}",
                "content": emp_status.get("market", "Đang cập nhật tình trạng thị trường..."),
                "badge": "Tuyển dụng", "time": r.last_updated, "type": "jobs"
            })

        articles = parse_json_column(r.research_articles, [])
        for art in articles:
            streams["academic"].append({
                "id": r.id, "title": art.get("title"),
                "content": f"Phân tích chuyên sâu từ nguồn xác thực. Trích dẫn bởi Maestro OS.",
                "badge": "Nghiên cứu", "time": r.last_updated, "type": "academic"
            })

        trends = parse_json_column(r.tech_trends, [])
        for t in trends:
            streams["trends"].append({
                "id": r.id, "title": t.get("name"),
                "content": t.get("update"),
                "badge": "Xu hướng", "time": r.last_updated, "type": "trends"
            })

    return {k: v[:12] for k, v in streams.items()}


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
async def get_history(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ResearchReportModel)
    if category and category != "all":
        query = query.filter(ResearchReportModel.categories.contains(category))

    reports = query.order_by(ResearchReportModel.id.desc()).all()
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


@agent_router.post("/chat")
async def chat_with_analyst(request: ChatRequest, db: Session = Depends(get_db)):
    query = db.query(ResearchReportModel)
    if request.category != "all":
        query = query.filter(ResearchReportModel.categories.contains(request.category))

    context_reports = query.order_by(ResearchReportModel.id.desc()).limit(10).all()
    engine = AgentEngine()
    answer = await engine.run_analyst(request.prompt, context_reports)

    return {"answer": answer}


def parse_json_column(data, default_value=None):
    if data is None:
        return default_value if default_value is not None else []
    if isinstance(data, (list, dict)):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return default_value if default_value is not None else []
    return default_value
