import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.maestro import MaestroOrchestrator
from app.database import SessionLocal

logger = logging.getLogger(__name__)


def run_daily_research():
    """Hàm wrapper để khởi tạo và đóng DB Session an toàn cho Job chạy ngầm"""
    db = SessionLocal()
    orchestrator = MaestroOrchestrator()
    topic = "Xu hướng công nghệ và AI mới nhất 2025"

    try:
        logger.info(f"⏰ CRONJOB: Đang chạy tự động nghiên cứu: {topic}")
        # Chạy hàm async trong môi trường sync của apscheduler
        asyncio.run(orchestrator.execute_workflow(topic, db))
    except Exception as e:
        logger.error(f"❌ CRONJOB LỖI: {str(e)}")
    finally:
        # BẮT BUỘC: Đóng kết nối DB sau khi job chạy xong
        db.close()


def start_cron_jobs():
    """Khởi động hệ thống đặt lịch"""
    scheduler = BackgroundScheduler()

    # Chạy hàm run_daily_research mỗi ngày vào lúc 00:00 (nửa đêm)
    scheduler.add_job(run_daily_research, 'cron', hour=0, minute=0)

    scheduler.start()
    logger.info("⏳ Scheduler đã khởi động. Sẽ tự động quét thị trường vào 0h mỗi ngày.")
