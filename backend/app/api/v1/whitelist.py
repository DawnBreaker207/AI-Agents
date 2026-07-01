import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import TopicWhitelist

router = APIRouter(prefix="/api/whitelist")
logger = logging.getLogger(__name__)


@router.get("")
async def get_whitelist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TopicWhitelist))
    return result.scalars().all()


@router.post("", status_code=201)
async def add_whitelist_topic(
    topic: str, boost_score: float = 1.5, force_keep: bool = False,
    db: AsyncSession = Depends(get_db)
):
    db.add(TopicWhitelist(topic=topic, boost_score=boost_score, force_keep=force_keep))
    await db.commit()
    return {"status": "created", "topic": topic}


@router.delete("/{topic_id}")
async def delete_whitelist_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(TopicWhitelist).where(TopicWhitelist.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Không tìm thấy topic.")
    await db.delete(topic)
    await db.commit()
    return {"status": "deleted"}
