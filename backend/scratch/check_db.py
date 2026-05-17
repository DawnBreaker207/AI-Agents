import asyncio
from app.database import AsyncSessionLocal
from app.models.source import SourceList
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(SourceList))
        sources = result.scalars().all()
        print(f"Total sources in DB: {len(sources)}")
        for s in sources:
            print(f" - {s.name} (Active: {s.is_active}) | {s.url}")

if __name__ == "__main__":
    asyncio.run(check())
