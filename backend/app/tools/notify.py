import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class DiscordNotifier:

    async def send_raw_feed(self, title: str, url: str):
        """Tầng 1 → #raw-feed: plain text, không embed"""
        if not settings.DISCORD_WEBHOOK_RAW_FEED:
            return
        payload = {"content": f"📥 [{title}]({url})"}
        await self._post(settings.DISCORD_WEBHOOK_RAW_FEED, payload)

    async def send_market_signal(self, title: str, url: str,
                                 impact_score: float, snippet: str = ""):
        """Tầng 2 → #market-signals: embed màu theo mức độ"""
        if not settings.DISCORD_WEBHOOK_MARKET_SIGNALS:
            return
        color = 0xFF0000 if impact_score >= 9 else 0xFF8C00
        payload = {
            "embeds": [{
                "title": f"⚠️ {title}",
                "description": snippet[:300] if snippet else "",
                "url": url,
                "color": color,
                "footer": {"text": f"Impact Score: {impact_score}/10"}
            }]
        }
        await self._post(settings.DISCORD_WEBHOOK_MARKET_SIGNALS, payload)

    async def send_strategic_report(self, title: str, url: str,
                                    executive_summary: str, vietnam_impact: str,
                                    action_items: list, source_citations: list = None):
        """Tầng 3 → #strategic-reports: Rich Embed đầy đủ với link dẫn chứng"""
        if not settings.DISCORD_WEBHOOK_STRATEGIC_REPORTS:
            return
        checklist = "\n".join([f"☐ {item}" for item in (action_items or [])[:5]])

        # Format citations thành list link Discord
        citations_text = ""
        if source_citations:
            citations_text = "\n".join(
                [f"[{i + 1}] {u}" for i, u in enumerate(source_citations[:5])]
            )

        fields = [
            {"name": "📋 Executive Summary",
             "value": (executive_summary or "N/A")[:500], "inline": False},
            {"name": "🇻🇳 Vietnam Market Impact",
             "value": (vietnam_impact or "N/A")[:400], "inline": False},
            {"name": "✅ Action Items",
             "value": checklist or "Không có", "inline": False},
        ]

        # Chỉ thêm field citations nếu có dữ liệu
        if citations_text:
            fields.append({
                "name": "🔗 Nguồn dẫn chứng",
                "value": citations_text[:500],
                "inline": False
            })

        payload = {
            "embeds": [{
                "title": f"📊 {title}",
                "url": url,
                "color": 0x00B4D8,
                "fields": fields,
                "footer": {"text": "TechScout Strategic Report"}
            }]
        }
        await self._post(settings.DISCORD_WEBHOOK_STRATEGIC_REPORTS, payload)

    async def _post(self, webhook_url: str, payload: dict):
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                res = await client.post(webhook_url, json=payload)
                res.raise_for_status()
            except Exception as e:
                logger.error(f"Discord notify error: {e}")
