import logging  # Import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.router import api_router
from app.config import settings
from app.worker.scheduler import start_cron_jobs
from database import engine, Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Hệ thống Agent đang khởi động ---")
    start_cron_jobs()
    yield
    logger.info("--- Hệ thống Agent đang đóng ---")


if not os.path.exists(settings.DATA_DIR):
    os.makedirs(settings.DATA_DIR)

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8888,
        reload=True)
