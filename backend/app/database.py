from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

Base = declarative_base()

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Lightweight migration cho SQLite đang có dữ liệu: thêm column mới nếu thiếu
        try:
            from sqlalchemy import text
            await conn.execute(text(
                "CREATE TABLE IF NOT EXISTS role_alias ("
                "id INTEGER PRIMARY KEY, canonical_role VARCHAR(200) NOT NULL, "
                "alias VARCHAR(200) NOT NULL UNIQUE, is_active BOOLEAN DEFAULT 1)"
            ))
            for ddl in (
                "ALTER TABLE pending_news ADD COLUMN gatekeeper_fail_count INTEGER DEFAULT 0",
                "ALTER TABLE source_list ADD COLUMN scan_priority VARCHAR(10) DEFAULT 'normal'",
                "ALTER TABLE research_reports ADD COLUMN category VARCHAR(50)",
            ):
                try:
                    await conn.execute(text(ddl))
                except Exception:
                    pass  # column đã tồn tại
        except Exception:
            pass
