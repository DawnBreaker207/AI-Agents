import logging
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models.source import SourceList
from app.models.category import TopicWhitelist, RoleAlias

logger = logging.getLogger(__name__)

RSS_SOURCES = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "priority_weight": 2.0},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss", "priority_weight": 1.8},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "priority_weight": 1.8},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "priority_weight": 1.7},
    {"name": "ZDNet", "url": "https://www.zdnet.com/news/rss.xml", "priority_weight": 1.5},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "priority_weight": 1.9},
    {"name": "IEEE Spectrum", "url": "https://feeds.feedburner.com/IeeeSpectrumFullText", "priority_weight": 1.7},
    {"name": "VentureBeat", "url": "https://venturebeat.com/feed/", "priority_weight": 1.6},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "priority_weight": 2.0},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news/rss.xml", "priority_weight": 2.0},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss/", "priority_weight": 2.0},
    {"name": "Hugging Face", "url": "https://huggingface.co/blog/feed.xml", "priority_weight": 1.9},
    {"name": "DeepMind Blog", "url": "https://deepmind.google/blog/rss/", "priority_weight": 1.9},
    {"name": "NVIDIA Dev Blog", "url": "https://developer.nvidia.com/blog//feed", "priority_weight": 1.6},
    {"name": "Hacker News Top", "url": "https://hnrss.org/frontpage?points=100", "priority_weight": 2.0},
    {"name": "GitHub Blog", "url": "https://github.blog/feed/", "priority_weight": 1.6},
    {"name": "InfoQ", "url": "https://feed.infoq.com/", "priority_weight": 1.7},
    {"name": "O'Reilly Radar", "url": "https://feeds.feedburner.com/oreilly/radar", "priority_weight": 1.7},
    {"name": "Reuters Tech", "url": "https://feeds.reuters.com/reuters/technologyNews", "priority_weight": 1.8},
    {"name": "CNBC Tech", "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html", "priority_weight": 1.7},
    {"name": "Layoffs.fyi", "url": "https://layoffs.fyi/feed/", "priority_weight": 2.0},
    {"name": "Spring Blog", "url": "https://spring.io/blog.atom", "priority_weight": 1.9},
    {"name": "Baeldung", "url": "https://www.baeldung.com/feed/", "priority_weight": 1.8},
    {"name": "Angular Blog", "url": "https://blog.angular.io/feed", "priority_weight": 1.9},
    {"name": "JetBrains Blog", "url": "https://blog.jetbrains.com/feed/", "priority_weight": 1.5},
    {"name": "DZone Java", "url": "https://feeds.dzone.com/java", "priority_weight": 1.6},
]

HIGH_PRIORITY_SOURCES = {"Layoffs.fyi", "Reuters Tech", "TechCrunch", "CNBC Tech"}

# 4.2 — alias mặc định cho Job Search
DEFAULT_ALIASES = [
    {"canonical_role": "Backend Developer", "alias": "Server-side Engineer"},
    {"canonical_role": "Backend Developer", "alias": "Backend Engineer"},
    {"canonical_role": "Frontend Developer", "alias": "Frontend Engineer"},
    {"canonical_role": "Frontend Developer", "alias": "Web Developer"},
    {"canonical_role": "DevOps Engineer", "alias": "Site Reliability Engineer"},
    {"canonical_role": "DevOps Engineer", "alias": "Platform Engineer"},
    {"canonical_role": "Data Engineer", "alias": "Big Data Engineer"},
    {"canonical_role": "QA Engineer", "alias": "Quality Assurance Engineer"},
    {"canonical_role": "QA Engineer", "alias": "Tester"},
    {"canonical_role": "Mobile Developer", "alias": "Android Developer"},
    {"canonical_role": "Mobile Developer", "alias": "iOS Developer"},
]

DEFAULT_WHITELIST = [
    # Công ty ưu tiên cho fast lane breaking news (force_keep=True để Scout bắt ngay)
    {"topic": "Oracle", "boost_score": 1.5, "force_keep": True},
    {"topic": "Google", "boost_score": 1.5, "force_keep": True},
    {"topic": "Meta", "boost_score": 1.5, "force_keep": True},
    {"topic": "Amazon", "boost_score": 1.5, "force_keep": True},
    {"topic": "Microsoft", "boost_score": 1.5, "force_keep": True},
    {"topic": "Apple", "boost_score": 1.5, "force_keep": True},
    {"topic": "Java Spring Boot", "boost_score": 2.0, "force_keep": True},    {"topic": "Java Spring Boot", "boost_score": 2.0, "force_keep": True},
    {"topic": "Angular", "boost_score": 2.0, "force_keep": True},
    {"topic": "Vietnam tech market", "boost_score": 2.0, "force_keep": True},
    {"topic": "thị trường công nghệ VN", "boost_score": 2.0, "force_keep": True},
    {"topic": "AI layoff", "boost_score": 1.8, "force_keep": False},
    {"topic": "mass layoff", "boost_score": 1.8, "force_keep": False},
    {"topic": "Anthropic", "boost_score": 1.7, "force_keep": False},
    {"topic": "OpenAI", "boost_score": 1.6, "force_keep": False},
    {"topic": "LLM", "boost_score": 1.5, "force_keep": False},
    {"topic": "microservices", "boost_score": 1.5, "force_keep": False},
]


async def auto_seed_db():
    await init_db()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(SourceList).limit(1))
        if result.scalar_one_or_none():
            # Backfill scan_priority cho DB đã có dữ liệu (idempotent)
            updated = 0
            for name in HIGH_PRIORITY_SOURCES:
                res = await db.execute(select(SourceList).where(SourceList.name == name))
                src = res.scalar_one_or_none()
                if src is not None and getattr(src, "scan_priority", None) != "high":
                    src.scan_priority = "high"
                    updated += 1
            if updated:
                await db.commit()
                logger.info(f"Backfill scan_priority: {updated} nguồn → 'high'.")
            # Backfill whitelist entries còn thiếu (vd công ty ưu tiên mới thêm)
            added = 0
            for wl in DEFAULT_WHITELIST:
                res = await db.execute(
                    select(TopicWhitelist).where(TopicWhitelist.topic == wl["topic"]))
                if res.scalar_one_or_none() is None:
                    db.add(TopicWhitelist(
                        topic=wl["topic"], boost_score=wl["boost_score"],
                        force_keep=wl["force_keep"], is_active=True))
                    added += 1
            if added:
                await db.commit()
                logger.info(f"Backfill whitelist: {added} topics mới.")
            # Backfill role_alias mặc định (4.2)
            added_alias = 0
            for al in DEFAULT_ALIASES:
                res = await db.execute(
                    select(RoleAlias).where(RoleAlias.alias == al["alias"]))
                if res.scalar_one_or_none() is None:
                    db.add(RoleAlias(canonical_role=al["canonical_role"],
                                     alias=al["alias"], is_active=True))
                    added_alias += 1
            if added_alias:
                await db.commit()
                logger.info(f"Backfill role_alias: {added_alias} alias mới.")
            return

        logger.info("Database trống. Bắt đầu tự động nạp (seeding) dữ liệu mẫu...")
        for src in RSS_SOURCES:
            db.add(SourceList(
                name=src["name"],
                url=src["url"],
                type="RSS",
                is_active=True,
                priority_weight=src["priority_weight"],
                scan_priority="high" if src["name"] in HIGH_PRIORITY_SOURCES else "normal",
            ))
        for wl in DEFAULT_WHITELIST:
            db.add(TopicWhitelist(
                topic=wl["topic"],
                boost_score=wl["boost_score"],
                force_keep=wl["force_keep"],
                is_active=True,
            ))
        for al in DEFAULT_ALIASES:
            db.add(RoleAlias(
                canonical_role=al["canonical_role"],
                alias=al["alias"],
                is_active=True,
            ))
        await db.commit()
        logger.info(f"Seeding hoàn tất: Đã nạp {len(RSS_SOURCES)} nguồn RSS và {len(DEFAULT_WHITELIST)} từ khóa ưu tiên.")
