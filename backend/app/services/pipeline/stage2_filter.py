import asyncio
import json
import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.brain import BrainService
from app.core.config import settings
from app.prompts.stage2_filter import STAGE2_FILTER_PROMPT
from app.models.news import PendingNews
from app.models.category import TopicWhitelist
from app.services.notify import DiscordNotifier
from pydantic import BaseModel

logger = logging.getLogger(__name__)

CRITICAL_KEYWORDS = [
    "mass layoff", "chapter 11", "bankruptcy", "acquisition",
    "merger", "IPO", "sập sàn", "phá sản", "mua lại"
]

LAYOFF_KEYWORDS = [
    "layoff", "layoffs", "lay off", "lays off", "laid off", "sa thải", "retrenchment",
    "job cut", "workforce reduction", "headcount"
]

CATEGORY_FALLBACK_TAGS = {
    "AI_RESEARCH": ["AI Research"],
    "LAYOFF": ["Layoff & Job Market"],
    "VN_MARKET": ["Vietnam Tech"],
    "DEV_TOOLS": ["Developer Tools"],
    "SECURITY": ["Security"],
    "BUSINESS": ["Business & Startup"],
    "OTHER": ["Tech News"],
}

KEYWORD_TAGS: list[tuple[str, str]] = [
    # AI & ML
    ("artificial intelligence", "AI"), ("machine learning", "Machine Learning"),
    ("deep learning", "Deep Learning"), ("large language model", "LLM"),
    ("llm", "LLM"), ("gpt", "GPT"), ("openai", "OpenAI"), ("chatgpt", "ChatGPT"),
    ("claude", "Claude"), ("anthropic", "Anthropic"), ("gemini", "Gemini"),
    ("copilot", "Copilot"), ("hugging face", "Hugging Face"),
    ("neural network", "Neural Network"), ("transformer model", "Transformer"),
    ("generative ai", "Generative AI"), ("genai", "Generative AI"),
    ("computer vision", "Computer Vision"), ("nlp", "NLP"),
    ("llama", "LLaMA"), ("mistral", "Mistral"),
    # Java & Spring
    ("java spring boot", "Spring Boot"), ("spring boot", "Spring Boot"),
    ("spring framework", "Spring Framework"), ("spring", "Spring"),
    ("hibernate", "Hibernate"), ("jakarta ee", "Jakarta EE"),
    ("jakarta", "Jakarta EE"), ("jvm", "JVM"), ("kotlin", "Kotlin"),
    ("microservices", "Microservices"), ("jpa", "JPA"),
    ("maven", "Maven"), ("gradle", "Gradle"), ("junit", "JUnit"),
    # Frontend
    ("react", "React"), ("angular", "Angular"), ("vue", "Vue.js"),
    ("typescript", "TypeScript"), ("javascript", "JavaScript"),
    ("frontend", "Frontend"), ("next.js", "Next.js"), ("nextjs", "Next.js"),
    ("tailwind", "Tailwind CSS"), ("webpack", "Webpack"),
    # DevOps & Cloud
    ("docker", "Docker"), ("kubernetes", "Kubernetes"), ("k8s", "Kubernetes"),
    ("aws", "AWS"), ("azure", "Azure"), ("gcp", "Google Cloud"),
    ("google cloud", "Google Cloud"), ("cloud computing", "Cloud Computing"),
    ("devops", "DevOps"), ("terraform", "Terraform"), ("ci/cd", "CI/CD"),
    ("linux", "Linux"), ("jenkins", "Jenkins"), ("github actions", "CI/CD"),
    # Data
    ("data science", "Data Science"), ("data scientist", "Data Science"),
    ("big data", "Big Data"), ("database", "Database"), ("sql", "SQL"),
    ("nosql", "NoSQL"), ("mongodb", "MongoDB"), ("postgresql", "PostgreSQL"),
    ("postgres", "PostgreSQL"), ("redis", "Redis"),
    # Job & Career
    ("hiring", "Hiring"), ("layoff", "Layoff"), ("laid off", "Layoff"),
    ("job cut", "Layoff"), ("sa thải", "Layoff"), ("recruitment", "Recruitment"),
    ("tuyển dụng", "Recruitment"), ("salary", "Salary"), ("lương", "Salary"),
    ("remote work", "Remote Work"), ("work from home", "Remote Work"),
    ("job market", "Job Market"), ("career", "Career"), ("việc làm", "Jobs"),
    ("internship", "Internship"), ("thực tập", "Internship"),
    # Security
    ("security", "Security"), ("cybersecurity", "Cybersecurity"),
    ("vulnerability", "Security"), ("ransomware", "Ransomware"),
    ("data breach", "Data Breach"), ("privacy", "Privacy"),
    # Business
    ("startup", "Startup"), ("ipo", "IPO"), ("acquisition", "Acquisition"),
    ("merger", "Merger"), ("fundraising", "Fundraising"),
    ("venture capital", "Venture Capital"), ("revenue", "Revenue"),
    # Programming Languages
    ("python", "Python"), ("rust", "Rust"), ("golang", "Go"), ("ruby", "Ruby"),
    ("swift", "Swift"), ("c++", "C++"), ("c#", "C#"), ("php", "PHP"),
    # Mobile
    ("android", "Android"), ("ios", "iOS"), ("flutter", "Flutter"),
    ("react native", "React Native"), ("swiftui", "SwiftUI"),
    # General Tech
    ("software", "Software"), ("developer", "Developer"),
    ("open source", "Open Source"), ("api", "API"),
    ("blockchain", "Blockchain"), ("web3", "Web3"), ("saas", "SaaS"),
    ("product launch", "Product Launch"), ("new release", "Release"),
    ("version", "Release"),
]


def _assign_topics_by_keywords(title: str, snippet: str | None) -> list[str]:
    combined = (title + " " + (snippet or "")).lower()
    topics = []
    for keyword, tag in KEYWORD_TAGS:
        if keyword.lower() in combined and tag not in topics:
            topics.append(tag)
    return topics


class FilterSignal(BaseModel):
    id: int
    title_vi: str = ""
    impact_score: float = 0.0
    category: str = "OTHER"
    reason: str = ""


class FilterResponse(BaseModel):
    signals: list[FilterSignal]


class GatekeeperStage:

    def __init__(self):
        self.brain = BrainService()
        self.notifier = DiscordNotifier()

    async def run(self, db: AsyncSession) -> list[int]:
        # Đếm tổng PENDING để đặt guard chống vòng lặp không hội tụ
        count_result = await db.execute(
            select(func.count()).select_from(PendingNews).where(PendingNews.status == "PENDING")
        )
        initial_pending = count_result.scalar_one_or_none() or 0
        if initial_pending == 0:
            logger.info("Gatekeeper: No PENDING articles found.")
            return []

        # ponytail: cap 200 tin/run, tránh chạy vô hạn nếu pipeline dừng lâu
        if initial_pending > 200:
            logger.warning(
                f"Gatekeeper: quá nhiều tin tồn đọng ({initial_pending}), "
                f"có thể pipeline đã dừng lâu — kiểm tra scheduler. "
                f"Chỉ xử lý 200 tin trong lần chạy này."
            )
        max_loops = min(initial_pending, 200) // settings.GATEKEEPER_BATCH_SIZE + 5

        wl_result = await db.execute(
            select(TopicWhitelist).where(TopicWhitelist.is_active == True)
        )
        whitelist = wl_result.scalars().all()

        all_urgent_ids: list[int] = []
        all_keep_ids: list[int] = []
        loops = 0
        while True:
            loops += 1
            if loops > max_loops:
                logger.warning(
                    "Gatekeeper: dừng sớm do nghi ngờ vòng lặp không hội tụ — kiểm tra model/API"
                )
                break
            result = await db.execute(
                select(PendingNews)
                .where(PendingNews.status == "PENDING")
                .order_by(PendingNews.published_at.desc().nullslast())
                .limit(settings.GATEKEEPER_BATCH_SIZE)
            )
            batch = result.scalars().all()
            if not batch:
                break
            urgent_ids, keep_ids = await self._process_batch(batch, whitelist, db)
            all_urgent_ids.extend(urgent_ids)
            all_keep_ids.extend(keep_ids)
            await asyncio.sleep(settings.LLM_CALL_DELAY)

        if all_urgent_ids or all_keep_ids:
            from app.core.events import news_broadcaster
            news_broadcaster.broadcast({"type": "new_news"})

        logger.info(
            f"Gatekeeper: {len(all_urgent_ids)} KEEP_URGENT, "
            f"{len(all_keep_ids)} KEEP, triggering Stage 3."
        )
        return all_urgent_ids + all_keep_ids

    async def _process_batch(self, batch, whitelist, db: AsyncSession) -> tuple[list[int], list[int]]:

        payload = [
            {"id": n.id, "title": n.title, "snippet": (n.snippet or "")[:300]}
            for n in batch
        ]

        system_instruction = (
            STAGE2_FILTER_PROMPT
            + "\n\nCRITICAL OVERRIDE: Bạn BẮt BUỘC phải trả về định dạng JSON theo cấu trúc mới sau đây thay vì cấu trúc cũ:\n"
            + "{\n"
            + '  "signals": [\n'
            + "    {\n"
            + '      "id": 1,\n'
            + '      "title_vi": "Tiêu đề bài báo được dịch sang Tiếng Việt chính xác và tự nhiên",\n'
            + '      "impact_score": 8.5,\n'
            + '      "category": "LAYOFF",\n'
            + '      "reason": "Mô tả lý do chấm điểm"\n'
            + "    }\n"
            + "  ]\n"
            + "}\n"
            + "LUỪ Ý:\n"
            + "- Trường 'title_vi': Dịch tiêu đề bài báo sang Tiếng Việt một cách tự nhiên, rõ ràng. Giữ nguyên tên riêng (tên công ty, người, sản phẩm). Nếu tiêu đề đã là tiếng Việt thì giữ nguyên.\n"
            + "- Trường 'category' hợp lệ: 'AI_RESEARCH' | 'LAYOFF' | 'VN_MARKET' | 'DEV_TOOLS' | 'SECURITY' | 'BUSINESS' | 'OTHER'.\n"
            + "- Trường 'id' phải trùng khớp chính xác với id của các tin tức đầu vào."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]

        response = await self.brain.call_ai_async(messages, model_tier="low", force_json=True)

        try:
            parsed = json.loads(response or "{}")
            validated = FilterResponse.model_validate(parsed)
            signals = validated.signals
        except Exception as e:
            logger.error(f"Gatekeeper: JSON parse/validation error: {e}")
            for news in batch:
                news.gatekeeper_fail_count = (news.gatekeeper_fail_count or 0) + 1
                if news.gatekeeper_fail_count >= 3:
                    news.status = "WATCH"  # an toàn hơn TRASH — không mất tin
                    logger.warning(
                        f"News #{news.id} chuyển WATCH sau {news.gatekeeper_fail_count} "
                        f"lần Gatekeeper lỗi JSON — có thể do model free trả sai format."
                    )
            await db.commit()
            signals = []

        urgent_ids: list[int] = []
        keep_ids: list[int] = []

        for signal in signals:
            news_id = signal.id
            score = signal.impact_score
            category = signal.category

            news = next((n for n in batch if n.id == news_id), None)
            if not news:
                continue

            # Tags bằng keyword matching — không cần AI
            matched = _assign_topics_by_keywords(news.title, news.snippet)

            combined = (news.title + " " + (news.snippet or "")).lower()

            for wl in whitelist:
                if wl.topic.lower() in combined:
                    if wl.topic not in matched:
                        matched.append(wl.topic)
                    score = min(score * wl.boost_score, 10.0)
                    if wl.force_keep and score < 8:
                        score = 8.0

            # Layoff đơn thuần cũng tính là khẩn cấp (không chỉ cụm "mass layoff")
            is_critical = any(kw in combined for kw in CRITICAL_KEYWORDS + LAYOFF_KEYWORDS)

            if not matched:
                matched = [CATEGORY_FALLBACK_TAGS.get(category, "Tech News")]

            news.impact_score = round(score, 2)
            news.category = category
            news.matched_topics = matched

            title_vi = signal.title_vi.strip()
            if title_vi:
                news.title = title_vi

            if score < 5:
                news.status = "TRASH"

            elif score < 8 and not any(
                    wl.force_keep for wl in whitelist if wl.topic.lower() in combined
            ):
                news.status = "WATCH"

            elif score >= 10 or (score >= 8 and is_critical):
                news.status = "KEEP_URGENT"
                urgent_ids.insert(0, news_id)

                if any(kw in combined for kw in LAYOFF_KEYWORDS):
                    await self.notifier.send_market_signal(
                        title=news.title, url=news.url,
                        impact_score=score, snippet=news.snippet or "",
                    )

            else:
                news.status = "KEEP"
                keep_ids.append(news_id)

                if any(kw in combined for kw in LAYOFF_KEYWORDS):
                    await self.notifier.send_market_signal(
                        title=news.title, url=news.url,
                        impact_score=score, snippet=news.snippet or "",
                    )

        await db.commit()
        return urgent_ids, keep_ids
