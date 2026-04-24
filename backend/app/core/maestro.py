import logging

from app.core.engine import AgentEngine

logger = logging.getLogger(__name__)

class MaestroOrchestrator:
    def __init__(self):
        self.agent_engine = AgentEngine()

    async def execute_workflow(self, prompt: str):
        logger.info(f"MaestroOrchestrator executing workflow for: '{prompt}'")
        report = await self.agent_engine.run(prompt)
        logger.info(f"Workflow completed. Report summary: {report.get('summary', 'N/A')}")
        return report