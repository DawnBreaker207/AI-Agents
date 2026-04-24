from apscheduler.schedulers.background import BackgroundScheduler

from app.core.maestro import MaestroOrchestrator


def start_cron_jobs():
    orchestrator = MaestroOrchestrator()
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        lambda: orchestrator.execute_workflow("https://example.com"),
        'cron', hour=0
    )

    scheduler.start()
