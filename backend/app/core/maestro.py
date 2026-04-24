import json

from sqlalchemy.orm import Session

from app.core.brain import BrainService
from app.models import AgentReportModel
from app.schemas import AgentReport


class MaestroOrchestrator:
    def __init__(self):
        self.brain = BrainService()

    def execute_workflow(self, user_goal: str):
        return self.brain.call_ai(user_goal)

    def process_and_save(self, url: str, db: Session) -> AgentReport:
        raw_result = self.execute_workflow(url)
        data_dict = json.loads(raw_result)
        report = AgentReport(**data_dict)

        db_report = AgentReportModel(
            title=report.title,
            key_points=json.dumps(report.key_points),
            sentiment=report.sentiment,
            token_usage_saved=report.token_usage_saved
        )

        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return report


maestro = MaestroOrchestrator()
