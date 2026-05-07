from sqlalchemy.orm import Session
from app.models.report import ResearchReportModel


def save_to_dashboard(db: Session, data: dict):
    """Tool: SAVE_TO_DASHBOARD"""
    new_report = ResearchReportModel(
        title=data.get("title", "Untitled"),
        content=data.get("summary", ""),
        impact_score=data.get("impact_score", 1),
        tags=data.get("tags", []),
        raw_analysis=data.get("raw_analysis"),
        source_url=data.get("url", "")
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report
