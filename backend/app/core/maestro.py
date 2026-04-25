import logging
from datetime import datetime, timezone, timedelta
from app.core.engine import AgentEngine
from app.models.report import ResearchReportModel

logger = logging.getLogger(__name__)


class MaestroOrchestrator:
    def __init__(self):
        self.agent_engine = AgentEngine()

    def is_outdated(self, report):
        if not report.last_updated:
            return True

        now = datetime.now(timezone.utc)
        last_updated = report.last_updated.replace(
            tzinfo=timezone.utc) if report.last_updated.tzinfo is None else report.last_updated
        return now - last_updated > timedelta(hours=24)

    async def execute_workflow(self, topic: str, db: Session, force_refresh: bool = False):
        #
        existing_report = db.query(ResearchReportModel).filter(
            ResearchReportModel.topic == topic
        ).first()

        #
        if existing_report and not force_refresh:
            if not self.is_outdated(existing_report):
                logger.info(f"Maestro: Trả về Cache cho: {topic}")
                return existing_report

        #
        logger.info(f"Maestro: Nghiên cứu mới cho: {topic}")
        report_data = await self.agent_engine.run(topic)
        #
        if existing_report:
            existing_report.summary = report_data.get("summary")
            existing_report.impact_score = report_data.get("impact_score", 0.0)
            existing_report.categories = report_data.get("categories", [])
            existing_report.regions = report_data.get("regions", [])
            existing_report.tech_trends = report_data.get("tech_trends", [])
            existing_report.employment_status = report_data.get("employment_status", {})
            existing_report.job_details = report_data.get("job_details", {})
            existing_report.research_articles = report_data.get("research_articles", [])
            existing_report.sources = report_data.get("sources", [])
            existing_report.sentiment = report_data.get("sentiment", "Trung tính")
            db.commit()
            db.refresh(existing_report)
            return existing_report
        else:
            new_report = ResearchReportModel(
                topic=topic,
                title=f"Báo cáo chiến lược: {topic}",
                summary=report_data.get("summary"),
                impact_score=report_data.get("impact_score", 0.0),
                categories=report_data.get("categories", []),
                regions=report_data.get("regions", []),
                tech_trends=report_data.get("tech_trends", []),
                employment_status=report_data.get("employment_status", {}),
                job_details=report_data.get("job_details", {}),
                research_articles=report_data.get("research_articles", []),
                sources=report_data.get("sources", []),
                sentiment=report_data.get("sentiment", "Trung tính"),
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_report)
            db.commit()
            db.refresh(new_report)
            return new_report
