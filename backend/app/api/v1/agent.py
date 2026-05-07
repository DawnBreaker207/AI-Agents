import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.core.engine import ChatEngine  # Import ChatEngine mới
from app.core.maestro import MaestroOrchestrator
from app.models.report import ResearchReportModel
from app.schemas.schemas import ChatRequest, ResearchReport
from core.utils import parse_json_column
from database import get_db
from schemas.schemas import ResearchRequest

api_router = APIRouter()
logger = logging.getLogger(__name__)


@api_router.get("/health", summary="Kiểm tra trạng thái của agent")
async def health_check():
    return {"status": "running", "agent": "GlobalTechTalentAgent-01"}


@api_router.post("/research", summary="Kích hoạt hệ thống TSI thực hiện nghiên cứu")
async def research_topic(request: ResearchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    orchestrator = MaestroOrchestrator()

    # Đẩy tác vụ nặng vào Background, API phản hồi ngay lập tức
    background_tasks.add_task(orchestrator.execute_workflow, request.topic, db)

    return {
        "status": "processing",
        "agent": "TechScout-01",
        "message": f"Hệ thống đang điều tra chiến lược: {request.topic}. Kết quả sẽ tự động lưu vào Dashboard."
    }


@api_router.post("/chat", summary="Hỏi đáp với Chuyên gia AI dựa trên dữ liệu báo cáo")
async def chat_with_analyst(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Query dữ liệu từ Database
    query = db.query(ResearchReportModel)

    # 2. Lọc theo Category nếu có (Tùy chọn)
    if request.category and request.category != "all":
        # Tìm kiếm tương đối trong cột tags (JSON)
        query = query.filter(ResearchReportModel.tags.contains([request.category]))

    # Lấy 5 báo cáo mới nhất làm ngữ cảnh
    context_reports = query.order_by(ResearchReportModel.created_at.desc()).limit(5).all()

    # 3. Khởi động ChatEngine
    engine = ChatEngine()
    answer = await engine.run_analyst(request.prompt, context_reports)

    return {"answer": answer}


@api_router.get("/history", response_model=List[ResearchReport], summary="Lấy lịch sử các báo cáo nghiên cứu")
async def get_history(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ResearchReportModel)
    if category and category != "all":
        query = query.filter(ResearchReportModel.categories.contains(category))

    reports = query.order_by(ResearchReportModel.id.desc()).all()
    results = []
    for r in reports:
        analysis = r.raw_analysis if r.raw_analysis else {}
        report_data = {
            "id": r.id,
            "title": r.title,
            "topic": getattr(r, "topic", r.title),  # Nếu không có topic, lấy title
            "summary": r.content,  # ĐỔI TỪ r.summary THÀNH r.content
            "impact_score": float(r.impact_score),
            "created_at": r.created_at,
            "last_updated": r.created_at,  # Lấy tạm created_at

            # Các trường Schema yêu cầu nhưng Model không có thì để mặc định
            "sentiment": "Trung tính",
            "categories": parse_json_column(r.tags),  # Map tags vào categories
            "regions": ["Việt Nam"],
            "sources": [r.source_url] if r.source_url else [],

            # Các trường chi tiết để trống nếu Model không có cột tương ứng
            "tech_trends": analysis.get("tech_trends", []),
            "employment_status": analysis.get("employment_status", {}),
            "job_details": analysis.get("job_details", {}),
            "research_articles": []
        }
        results.append(ResearchReport.model_validate(report_data))
    return results


@api_router.get("/report/{report_id}", response_model=ResearchReport, summary="Lấy chi tiết một báo cáo nghiên cứu")
async def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    r = db.query(ResearchReportModel).filter(ResearchReportModel.id == report_id).first()

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
        "summary": r.content,  # ĐỔI TỪ r.summary THÀNH r.content
        "impact_score": float(r.impact_score),
        "created_at": r.created_at,
        "last_updated": r.created_at,
        "sentiment": analysis.get("sentiment", "Trung tính"),
        "categories": parse_json_column(r.tags),
        "regions": ["Việt Nam"],
        "sources": [r.source_url] if r.source_url else [],
        "tech_trends": analysis.get("tech_trends", []),
        "employment_status": analysis.get("employment_status", {}),
        "job_details": analysis.get("job_details", {}),
        "research_articles": []
    }

    return ResearchReport.model_validate(report_data)



