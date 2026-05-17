import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.v1.agent import api_router
from app.core.config import settings
from app.core.seeder import auto_seed_db
from app.database import init_db
from app.worker.scheduler import start_cron_jobs

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Hệ thống Agent đang khởi động ---")
    await init_db()
    await auto_seed_db()
    start_cron_jobs()
    yield
    logger.info("--- Hệ thống Agent đang đóng ---")


from fastapi.middleware.cors import CORSMiddleware

if not os.path.exists(settings.DATA_DIR):
    os.makedirs(settings.DATA_DIR)

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8888,
        reload=True)
