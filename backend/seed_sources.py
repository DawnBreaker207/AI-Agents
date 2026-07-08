"""
Chạy: python seed_sources.py
Mục đích: Thêm danh sách nguồn RSS và whitelist topic vào DB
"""
import asyncio
from app.database import AsyncSessionLocal, init_db
from app.models.source import SourceList
from app.models.category import TopicWhitelist
from sqlalchemy import select

RSS_SOURCES = [
    # =============================================================
    # === TECH & CÔNG NGHỆ GLOBAL — uy tín, tin gốc
    # =============================================================
    {"name": "TechCrunch",        "url": "https://techcrunch.com/feed/",                               "priority_weight": 2.0},
    {"name": "The Verge",         "url": "https://www.theverge.com/rss/index.xml",                    "priority_weight": 1.8},
    {"name": "Ars Technica",      "url": "https://feeds.arstechnica.com/arstechnica/index",            "priority_weight": 1.8},
    {"name": "Wired",             "url": "https://www.wired.com/feed/rss",                             "priority_weight": 1.8},
    {"name": "MIT Tech Review",   "url": "https://www.technologyreview.com/feed/",                    "priority_weight": 1.9},
    {"name": "IEEE Spectrum",     "url": "https://feeds.feedburner.com/IeeeSpectrumFullText",          "priority_weight": 1.7},
    {"name": "VentureBeat",       "url": "https://venturebeat.com/feed/",                             "priority_weight": 1.6},
    {"name": "The Next Web",      "url": "https://thenextweb.com/feed",                               "priority_weight": 1.6},
    {"name": "Engadget",          "url": "https://www.engadget.com/rss.xml",                          "priority_weight": 1.5},
    {"name": "CNET",              "url": "https://www.cnet.com/rss/all/",                             "priority_weight": 1.5},
    {"name": "ZDNet",             "url": "https://www.zdnet.com/news/rss.xml",                        "priority_weight": 1.5},

    # =============================================================
    # === SẢN PHẨM & PHẦN MỀM MỚI — release, launch, update
    # =============================================================
    {"name": "Product Hunt",      "url": "https://www.producthunt.com/feed?category=tech",             "priority_weight": 1.8},
    {"name": "Google Blog",       "url": "https://blog.google/feed/",                                 "priority_weight": 1.7},
    {"name": "Microsoft Blog",    "url": "https://blogs.microsoft.com/feed/",                         "priority_weight": 1.7},
    {"name": "Apple Newsroom",    "url": "https://www.apple.com/newsroom/rss-feed.rss",               "priority_weight": 1.7},
    {"name": "AWS Blog",          "url": "https://aws.amazon.com/blogs/aws/feed/",                    "priority_weight": 1.6},
    {"name": "Chrome Dev Blog",   "url": "https://developer.chrome.com/feeds/blog",                   "priority_weight": 1.5},
    {"name": "Mozilla Hacks",     "url": "https://hacks.mozilla.org/feed/",                           "priority_weight": 1.5},

    # =============================================================
    # === AI RESEARCH LABS — OpenAI, Anthropic, DeepMind, Meta...
    # =============================================================
    {"name": "OpenAI Blog",       "url": "https://openai.com/blog/rss/",                              "priority_weight": 2.0},
    {"name": "Anthropic News",    "url": "https://www.anthropic.com/news/rss.xml",                    "priority_weight": 2.0},
    {"name": "Google AI Blog",    "url": "https://blog.google/technology/ai/rss/",                    "priority_weight": 2.0},
    {"name": "DeepMind Blog",     "url": "https://deepmind.google/blog/rss/",                         "priority_weight": 1.9},
    {"name": "Meta AI Research",  "url": "https://ai.meta.com/blog/rss/",                             "priority_weight": 1.8},
    {"name": "Apple ML Research", "url": "https://machinelearning.apple.com/rss",                     "priority_weight": 1.7},
    {"name": "Hugging Face",      "url": "https://huggingface.co/blog/feed.xml",                      "priority_weight": 1.9},
    {"name": "NVIDIA Dev Blog",   "url": "https://developer.nvidia.com/blog/feed",                    "priority_weight": 1.6},

    # =============================================================
    # === DEVELOPER & ENGINEERING BLOGS
    # =============================================================
    {"name": "GitHub Blog",       "url": "https://github.blog/feed/",                                 "priority_weight": 1.6},
    {"name": "Stack Overflow",    "url": "https://stackoverflow.blog/feed/",                          "priority_weight": 1.8},
    {"name": "Dev.to",            "url": "https://dev.to/feed",                                       "priority_weight": 1.6},
    {"name": "Cloudflare Blog",   "url": "https://blog.cloudflare.com/rss/",                          "priority_weight": 1.7},
    {"name": "JetBrains Blog",    "url": "https://blog.jetbrains.com/feed/",                          "priority_weight": 1.5},
    {"name": "InfoQ",             "url": "https://feed.infoq.com/",                                   "priority_weight": 1.7},
    {"name": "O'Reilly Radar",    "url": "https://feeds.feedburner.com/oreilly/radar",                "priority_weight": 1.7},

    # =============================================================
    # === JAVA ECOSYSTEM — framework, release, best practices
    # =============================================================
    {"name": "Spring Blog",         "url": "https://spring.io/blog.atom",                                "priority_weight": 1.9},
    {"name": "Baeldung",            "url": "https://www.baeldung.com/feed/",                             "priority_weight": 1.8},
    {"name": "Inside Java",         "url": "https://inside.java/feed.xml",                               "priority_weight": 1.8},
    {"name": "Foojay.io",           "url": "https://foojay.io/feed/",                                    "priority_weight": 1.7},
    {"name": "Java Magazine",       "url": "https://blogs.oracle.com/javamagazine/feed",                 "priority_weight": 1.7},
    {"name": "JAXenter",            "url": "https://jaxenter.com/feed",                                  "priority_weight": 1.6},
    {"name": "InfoWorld Java",      "url": "https://www.infoworld.com/category/java/index.rss",          "priority_weight": 1.6},
    {"name": "Java Code Geeks",     "url": "https://www.javacodegeeks.com/feed",                          "priority_weight": 1.5},
    {"name": "DZone Java",          "url": "https://feeds.dzone.com/java",                               "priority_weight": 1.6},

    # =============================================================
    # === FRAMEWORK / LANGUAGE SPECIFIC BLOGS (non-Java)
    # =============================================================
    {"name": "Angular Blog",      "url": "https://blog.angular.io/feed",                              "priority_weight": 1.9},
    {"name": "React Blog",        "url": "https://react.dev/blog/rss.xml",                            "priority_weight": 1.8},
    {"name": "Python Blog",       "url": "https://blog.python.org/feeds/posts/default",               "priority_weight": 1.5},
    {"name": "Rust Blog",         "url": "https://blog.rust-lang.org/feed.xml",                       "priority_weight": 1.6},

    # =============================================================
    # === TIN TỨC DOANH NGHIỆP & KINH TẾ — layoff, M&A, tài chính
    # =============================================================
    {"name": "Reuters Tech",      "url": "https://feeds.reuters.com/reuters/technologyNews",           "priority_weight": 1.9},
    {"name": "Bloomberg Tech",    "url": "https://feeds.bloomberg.com/markets/news.rss",               "priority_weight": 1.9},
    {"name": "CNBC Tech",         "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html",       "priority_weight": 1.8},
    {"name": "Financial Times Tech", "url": "https://www.ft.com/technology?format=rss",               "priority_weight": 1.8},
    {"name": "Business Insider Tech", "url": "https://www.businessinsider.com/rss/tech",              "priority_weight": 1.7},
    {"name": "Fortune Tech",      "url": "https://fortune.com/feed/fortune-tech",                     "priority_weight": 1.7},
    {"name": "Forbes Tech",       "url": "https://www.forbes.com/technology/feed/",                   "priority_weight": 1.7},
    {"name": "Axios Tech",        "url": "https://www.axios.com/feeds/tech/",                         "priority_weight": 1.7},
    {"name": "The Register",      "url": "https://www.theregister.com/headlines.rss",                 "priority_weight": 1.6},
    {"name": "Layoffs.fyi",       "url": "https://layoffs.fyi/feed/",                                 "priority_weight": 2.0},

    # =============================================================
    # === VIỆC LÀM & THỊ TRƯỜNG NHÂN LỰC GLOBAL
    # =============================================================
    {"name": "LinkedIn Blog",         "url": "https://www.linkedin.com/blog/rss",                       "priority_weight": 1.8},
    {"name": "Glassdoor Blog",        "url": "https://www.glassdoor.com/blog/feed/",                    "priority_weight": 1.6},
    {"name": "Indeed Blog",           "url": "https://www.indeed.com/blog/feed/",                       "priority_weight": 1.5},
    {"name": "Hacker News Who's Hiring", "url": "https://hnrss.org/jobs?points=1",                     "priority_weight": 1.9},
    {"name": "Dice Insights",         "url": "https://www.dice.com/insights/feed/",                     "priority_weight": 1.5},
    {"name": "Remote OK",             "url": "https://remoteok.com/feed",                               "priority_weight": 1.7},
    {"name": "We Work Remotely",      "url": "https://weworkremotely.com/feed",                         "priority_weight": 1.6},

    # =============================================================
    # === JOB LISTINGS — việc làm thực tế (RSS feed)
    # =============================================================
    {"name": "Stack Overflow Jobs",   "url": "https://stackoverflow.com/jobs/feed",                     "priority_weight": 1.9},
    {"name": "Indeed Jobs (Software)", "url": "https://www.indeed.com/rss?q=software+developer&l=",    "priority_weight": 1.7},
    {"name": "Indeed Jobs (Java)",     "url": "https://www.indeed.com/rss?q=java&l=",                  "priority_weight": 1.7},
    {"name": "Indeed Jobs (DevOps)",   "url": "https://www.indeed.com/rss?q=devops&l=",                "priority_weight": 1.6},
    {"name": "Indeed Jobs (Data)",     "url": "https://www.indeed.com/rss?q=data+scientist&l=",        "priority_weight": 1.6},

    # =============================================================
    # === CỘNG ĐỒNG & CURATION
    # =============================================================
    {"name": "Hacker News Top",   "url": "https://hnrss.org/frontpage?points=100",                     "priority_weight": 2.0},
    {"name": "Lobsters",          "url": "https://lobste.rs/rss",                                      "priority_weight": 1.7},
    {"name": "Echo JS",           "url": "https://echojs.com/feed",                                    "priority_weight": 1.4},

    # =============================================================
    # === VIỆT NAM (giữ lại vài nguồn gốc, có giá trị riêng)
    # =============================================================
    {"name": "CafeF - Thị trường",  "url": "https://cafef.vn/thi-truong.rss",                         "priority_weight": 1.8},
    {"name": "Brands Vietnam",      "url": "https://brandsvietnam.com/rss",                           "priority_weight": 1.5},
    {"name": "ITViec Blog",         "url": "https://itviec.com/blog/feed/",                           "priority_weight": 1.8},
    {"name": "TopDev Blog",         "url": "https://topdev.vn/blog/feed/",                            "priority_weight": 1.8},
    {"name": "VietnamWorks Blog",   "url": "https://www.vietnamworks.com/hr-insights/feed/",          "priority_weight": 1.7},
]

DEFAULT_WHITELIST = [
    # ==========================
    # === FORCE_KEEP (luôn vào Stage 3) ===
    # ==========================
    {"topic": "Java Spring Boot", "boost_score": 2.0, "force_keep": True},
    {"topic": "Angular", "boost_score": 2.0, "force_keep": True},
    {"topic": "Vietnam tech market", "boost_score": 2.0, "force_keep": True},
    {"topic": "thị trường công nghệ VN", "boost_score": 2.0, "force_keep": True},

    # ==========================
    # === AI & RESEARCH ===
    # ==========================
    {"topic": "AI layoff", "boost_score": 1.8, "force_keep": False},
    {"topic": "mass layoff", "boost_score": 1.8, "force_keep": False},
    {"topic": "Anthropic", "boost_score": 1.8, "force_keep": False},
    {"topic": "OpenAI", "boost_score": 1.8, "force_keep": False},
    {"topic": "GPT", "boost_score": 1.6, "force_keep": False},
    {"topic": "LLM", "boost_score": 1.6, "force_keep": False},
    {"topic": "Claude", "boost_score": 1.7, "force_keep": False},
    {"topic": "Gemini", "boost_score": 1.6, "force_keep": False},
    {"topic": "deep learning", "boost_score": 1.5, "force_keep": False},
    {"topic": "machine learning", "boost_score": 1.5, "force_keep": False},

    # ==========================
    # === JAVA & SPRING ===
    # ==========================
    {"topic": "Java", "boost_score": 1.7, "force_keep": False},
    {"topic": "Spring Framework", "boost_score": 1.8, "force_keep": False},
    {"topic": "Hibernate", "boost_score": 1.5, "force_keep": False},
    {"topic": "Jakarta EE", "boost_score": 1.5, "force_keep": False},
    {"topic": "Kotlin", "boost_score": 1.5, "force_keep": False},

    # ==========================
    # === DEV TOOLS & FRAMEWORK ===
    # ==========================
    {"topic": "React", "boost_score": 1.7, "force_keep": False},
    {"topic": "microservices", "boost_score": 1.5, "force_keep": False},
    {"topic": "Docker", "boost_score": 1.5, "force_keep": False},
    {"topic": "Kubernetes", "boost_score": 1.6, "force_keep": False},
    {"topic": "Python", "boost_score": 1.5, "force_keep": False},
    {"topic": "TypeScript", "boost_score": 1.5, "force_keep": False},
    {"topic": "Rust", "boost_score": 1.6, "force_keep": False},
    {"topic": "cloud computing", "boost_score": 1.5, "force_keep": False},

    # ==========================
    # === VIỆC LÀM & TUYỂN DỤNG ===
    # ==========================
    {"topic": "IT job market", "boost_score": 1.8, "force_keep": False},
    {"topic": "remote work", "boost_score": 1.7, "force_keep": False},
    {"topic": "tuyển dụng IT", "boost_score": 1.7, "force_keep": False},
    {"topic": "hiring", "boost_score": 1.6, "force_keep": False},
    {"topic": "recruitment", "boost_score": 1.5, "force_keep": False},
    {"topic": "IT salary", "boost_score": 1.6, "force_keep": False},
    {"topic": "lương IT", "boost_score": 1.6, "force_keep": False},
    {"topic": "tech talent", "boost_score": 1.5, "force_keep": False},
    {"topic": "job market", "boost_score": 1.5, "force_keep": False},
    {"topic": "career", "boost_score": 1.4, "force_keep": False},
    {"topic": "việc làm IT", "boost_score": 1.6, "force_keep": False},
    {"topic": "nhân lực công nghệ", "boost_score": 1.5, "force_keep": False},

    # ==========================
    # === CÔNG NGHỆ VIỆT NAM ===
    # ==========================
    {"topic": "startup Việt", "boost_score": 1.5, "force_keep": False},
    {"topic": "chuyển đổi số", "boost_score": 1.5, "force_keep": False},
    {"topic": "digital transformation", "boost_score": 1.5, "force_keep": False},
]


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        source_count = 0
        for src in RSS_SOURCES:
            exists = await db.execute(
                select(SourceList).where(SourceList.url == src["url"])
            )
            if not exists.scalar_one_or_none():
                db.add(SourceList(
                    name=src["name"],
                    url=src["url"],
                    type="RSS",
                    is_active=True,
                    priority_weight=src["priority_weight"],
                ))
                source_count += 1

        wl_count = 0
        for wl in DEFAULT_WHITELIST:
            exists = await db.execute(
                select(TopicWhitelist).where(TopicWhitelist.topic == wl["topic"])
            )
            if not exists.scalar_one_or_none():
                db.add(TopicWhitelist(
                    topic=wl["topic"],
                    boost_score=wl["boost_score"],
                    force_keep=wl["force_keep"],
                    is_active=True,
                ))
                wl_count += 1

        await db.commit()
        print(f"Seed completed: {source_count} RSS sources, {wl_count} whitelist topics added.")


if __name__ == "__main__":
    asyncio.run(seed())
