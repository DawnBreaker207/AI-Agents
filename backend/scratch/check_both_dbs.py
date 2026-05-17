import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.source import SourceList
from sqlalchemy import select
import os

async def check(db_path):
    url = f"sqlite+aiosqlite:///{db_path}"
    print(f"Checking DB: {db_path}")
    engine = create_async_engine(url)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as db:
        try:
            result = await db.execute(select(SourceList))
            sources = result.scalars().all()
            print(f"Total sources: {len(sources)}")
        except Exception as e:
            print(f"Error: {e}")
    await engine.dispose()

async def run():
    await check("./data/app.db")

if __name__ == "__main__":
    asyncio.run(run())
