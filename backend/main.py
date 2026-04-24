import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import router as agent_router
from app.worker.scheduler import start_cron_jobs
from database import engine, Base

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Hệ thống Agent đang khởi động ---")
    start_cron_jobs()
    yield
    print("--- Hệ thống Agent đang đóng ---")


if not os.path.exists('data'):
    os.makedirs('data')
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=os.getenv("APP_NAME"),
    lifespan=lifespan
)
app.include_router(agent_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8888,
        reload=True)
