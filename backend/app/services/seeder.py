import logging
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models.source import SourceList
from app.models.category import TopicWhitelist

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

DEFAULT_WHITELIST = [
    {"topic": "Java Spring Boot", "boost_score": 2.0, "force_keep": True},
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
            return

        logger.info("Database trống. Bắt đầu tự động nạp (seeding) dữ liệu mẫu...")
        for src in RSS_SOURCES:
            db.add(SourceList(
                name=src["name"],
                url=src["url"],
                type="RSS",
                is_active=True,
                priority_weight=src["priority_weight"],
            ))
        for wl in DEFAULT_WHITELIST:
            db.add(TopicWhitelist(
                topic=wl["topic"],
                boost_score=wl["boost_score"],
                force_keep=wl["force_keep"],
                is_active=True,
            ))
        await db.commit()
        logger.info(f"Seeding hoàn tất: Đã nạp {len(RSS_SOURCES)} nguồn RSS và {len(DEFAULT_WHITELIST)} từ khóa ưu tiên.")
