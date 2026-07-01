import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.news import PendingNews
from app.models.report import ResearchReport
from app.schemas.report import ResearchReportSchema
from app.schemas.common import APIResponse
from app.utils.helpers import parse_json_column

router = APIRouter()
logger = logging.getLogger(__name__)


def _sanitize_report_field(value) -> str | None:
    if not value:
        return None

    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("[", "{")):
            try:
                value = json.loads(stripped)
            except Exception:
                return stripped
        else:
            return stripped

    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                trend = item.get("trend") or item.get("name") or item.get("title") or ""
                desc = item.get("description") or item.get("update") or item.get("details") or ""
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


@router.get("/history", summary="Get research report history")
async def get_history(category: str | None = None, db: AsyncSession = Depends(get_db)):
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


@router.get("/report/{report_id}", summary="Get report detail")
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


@router.get("/api/reports/strategic")
async def get_strategic_reports(
    page: int = 1, size: int = 20,
    db: AsyncSession = Depends(get_db)
):
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


@router.get("/api/reports/{report_id}")
async def get_report_detail(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
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
