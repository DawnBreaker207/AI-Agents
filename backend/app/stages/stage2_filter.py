import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.brain import BrainService
from app.core.prompt import STAGE2_FILTER_PROMPT
from app.models import PendingNews, TopicWhitelist
from app.tools.notify import DiscordNotifier
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class FilterSignal(BaseModel):
    id: int
    title_vi: str = ""
    impact_score: float = 0.0
    category: str = "OTHER"
    matched_topics: list[str] = Field(default_factory=list)
    reason: str = ""

class FilterResponse(BaseModel):
    signals: list[FilterSignal]

CRITICAL_KEYWORDS = [
    "mass layoff", "chapter 11", "bankruptcy", "acquisition",
    "merger", "IPO", "sập sàn", "phá sản", "mua lại"
]

LAYOFF_KEYWORDS = [
    "layoff", "laid off", "sa thải", "retrenchment",
    "job cut", "workforce reduction", "headcount"
]


class GatekeeperStage:

    def __init__(self):
        self.brain = BrainService()
        self.notifier = DiscordNotifier()

    async def run(self, db: AsyncSession) -> list[int]:
        """Fetch pending news, score impact using a low-tier model, and filter entries."""
        result = await db.execute(
            select(PendingNews).where(PendingNews.status == "PENDING").limit(25)
        )
        batch = result.scalars().all()
        if not batch:
            logger.info("Gatekeeper: No PENDING articles found.")
            return []

        # Load whitelist topics once beforehand to optimize performance
        wl_result = await db.execute(
            select(TopicWhitelist).where(TopicWhitelist.is_active == True)
        )
        whitelist = wl_result.scalars().all()

        # Send only fundamental metadata to keep token costs to a minimum
        payload = [
            {"id": n.id, "title": n.title, "snippet": (n.snippet or "")[:300]}
            for n in batch
        ]

        # Force a structured JSON schema in the model response
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
            + '      "matched_topics": ["AI layoff", "Vietnam tech market"],\n'
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
            parsed = json.loads(response)
            validated = FilterResponse.model_validate(parsed)
            signals = validated.signals
        except Exception as e:
            logger.error(f"Gatekeeper: JSON parse/validation error: {e}")
            signals = []

        urgent_ids = []
        keep_ids = []

        for signal in signals:
            news_id = signal.id
            score = signal.impact_score
            category = signal.category
            matched = signal.matched_topics

            news = next((n for n in batch if n.id == news_id), None)
            if not news:
                continue

            combined = (news.title + " " + (news.snippet or "")).lower()

            # Apply whitelist boosts and limit the maximum score strictly to 10.0
            for wl in whitelist:
                if wl.topic.lower() in combined:
                    if wl.topic not in matched:
                        matched.append(wl.topic)
                    score = min(score * wl.boost_score, 10.0)
                    if wl.force_keep and score < 8:
                        score = 8.0  # Elevate automatically to the minimum deep analysis threshold (KEEP)

            is_critical = any(kw in combined for kw in CRITICAL_KEYWORDS)

            news.impact_score = round(score, 2)
            news.category = category
            news.matched_topics = matched

            # Persist Vietnamese title if provided by AI (fallback to original title)
            title_vi = signal.title_vi.strip()
            if title_vi:
                news.title = title_vi

            # Categorize the article's pipeline status based on score thresholds
            if score < 5:
                news.status = "TRASH"

            elif score < 8 and not any(
                    wl.force_keep for wl in whitelist if wl.topic.lower() in combined
            ):
                # WATCH: Informative but below full report requirements
                news.status = "WATCH"

            elif score >= 10 or (score >= 8 and is_critical):
                # KEEP_URGENT: Trigger immediate analysis bypass
                news.status = "KEEP_URGENT"
                urgent_ids.insert(0, news_id)

                if any(kw in combined for kw in LAYOFF_KEYWORDS):
                    await self.notifier.send_market_signal(
                        title=news.title, url=news.url,
                        impact_score=score, snippet=news.snippet or "",
                    )

            else:
                # KEEP: Queue for sequential deep analysis (Stage 3)
                news.status = "KEEP"
                keep_ids.append(news_id)

                if any(kw in combined for kw in LAYOFF_KEYWORDS):
                    await self.notifier.send_market_signal(
                        title=news.title, url=news.url,
                        impact_score=score, snippet=news.snippet or "",
                    )

        await db.commit()
        if urgent_ids or keep_ids:
            from app.core.events import news_broadcaster
            news_broadcaster.broadcast({"type": "new_news"})
            
        logger.info(
            f"Gatekeeper: {len(urgent_ids)} KEEP_URGENT, "
            f"{len(keep_ids)} KEEP, triggering Stage 3."
        )
        return urgent_ids + keep_ids