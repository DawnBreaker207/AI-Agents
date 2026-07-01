import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.report import ResearchReport
from app.schemas.common import ChatRequest, APIResponse
from app.services.engine import ChatEngine

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", summary="Chat with AI Analyst based on report data")
async def chat_with_analyst(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    query = select(ResearchReport)
    query = query.order_by(ResearchReport.created_at.desc()).limit(5)
    result = await db.execute(query)
    context_reports = result.scalars().all()

    engine = ChatEngine()
    answer = await engine.run_analyst(request.prompt, context_reports)

    return APIResponse(
        message="Phản hồi từ AI Analyst",
        data={"answer": answer}
    )
