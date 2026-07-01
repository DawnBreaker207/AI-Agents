import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.source import SourceList

router = APIRouter(prefix="/api/sources")
logger = logging.getLogger(__name__)


@router.get("")
async def get_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SourceList).order_by(SourceList.id.desc()))
    return result.scalars().all()


@router.put("/{source_id}/toggle")
async def toggle_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SourceList).where(SourceList.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Không tìm thấy nguồn.")
    source.is_active = not source.is_active
    await db.commit()
    return {"id": source_id, "is_active": source.is_active}
