from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

from app.core.maestro import MaestroOrchestrator


def start_cron_jobs():
    orchestrator = MaestroOrchestrator()
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        lambda: asyncio.run(orchestrator.execute_workflow("Hãy nghiên cứu về các xu hướng công nghệ mới nhất.")),
        'cron', hour=0
    )

    scheduler.start()
