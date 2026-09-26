import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import init_db
from app.services.seeder import auto_seed_db
from app.services.pipeline.orchestrator import start_cron_jobs

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


if not os.path.exists(settings.DATA_DIR):
    os.makedirs(settings.DATA_DIR)

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routes
from app.api.v1.health import router as health_router
from app.api.v1.news import router as news_router
from app.api.v1.reports import router as reports_router
from app.api.v1.sources import router as sources_router
from app.api.v1.whitelist import router as whitelist_router
from app.api.v1.aliases import router as aliases_router
from app.api.v1.pipeline import router as pipeline_router
from app.api.v1.metrics import router as metrics_router

app.include_router(health_router)
app.include_router(news_router)
app.include_router(reports_router)
app.include_router(sources_router)
app.include_router(whitelist_router)
app.include_router(aliases_router)
app.include_router(pipeline_router)
app.include_router(metrics_router)

from app.api.v1.jobs import router as jobs_router
app.include_router(jobs_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8888,
        reload=True)
