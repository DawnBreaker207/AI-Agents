import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import RoleAlias

router = APIRouter(prefix="/api/aliases")
logger = logging.getLogger(__name__)


@router.get("")
async def get_aliases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RoleAlias).where(RoleAlias.is_active == True))
    return result.scalars().all()


@router.post("", status_code=201)
async def add_alias(
    canonical_role: str, alias: str,
    db: AsyncSession = Depends(get_db)
):
    exists = await db.execute(select(RoleAlias).where(RoleAlias.alias == alias))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Alias đã tồn tại.")
    db.add(RoleAlias(canonical_role=canonical_role, alias=alias))
    await db.commit()
    return {"status": "created", "alias": alias}


@router.delete("/{alias_id}")
async def delete_alias(alias_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RoleAlias).where(RoleAlias.id == alias_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy alias.")
    await db.delete(item)
    await db.commit()
    return {"status": "deleted"}
