import json
import logging
import re

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.brain import BrainService
from app.core.config import settings
from app.prompts.stage3_react import STAGE3_REACT_PROMPT as STAGE3_DEEP_PROMPT
from app.models.news import PendingNews
from app.models.report import ResearchReport
from app.services.notify import DiscordNotifier
from app.utils.helpers import parse_xml_tag

logger = logging.getLogger(__name__)

_JUNK_CONTENT_SIGNALS = [
    "404", "page not found", "không tìm thấy trang",
    "access denied", "403 forbidden",
    "enable javascript", "please enable cookies",
    "subscribe to continue", "sign in to read",
    "just a moment", "checking your browser",
]


async def _fetch_full_content(url: str) -> tuple[str, bool, str]:
    jina_url = f"https://r.jina.ai/{url}"
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            res = await client.get(
                jina_url,
                headers={"Accept": "text/markdown", "User-Agent": "TechScout/1.0"},
                follow_redirects=True,
            )
            if res.status_code >= 400:
                return "", False, f"Jina HTTP {res.status_code}"

            content = res.text.strip()

            if len(content) < settings.MIN_CONTENT_LENGTH:
                return "", False, f"Content too short ({len(content)} characters)"

            content_lower = content.lower()
            for signal in _JUNK_CONTENT_SIGNALS:
                if signal in content_lower:
                    return "", False, f"Junk or challenge page detected: '{signal}'"

            return content[:settings.WEB_CONTENT_MAX_LENGTH], True, ""

        except httpx.TimeoutException:
            return "", False, "Jina timeout"
        except Exception as e:
            return "", False, f"Jina error: {type(e).__name__}: {e}"


class DeepAnalysisStage:

    def __init__(self):
        self.brain = BrainService()

    async def _run_react_loop(self, filtered_signals: list) -> dict:
        messages = [
            {"role": "system", "content": STAGE3_DEEP_PROMPT},
            {"role": "user", "content": json.dumps(filtered_signals, ensure_ascii=False)},
        ]

        final_result = {"status": "error", "analysis": "ReAct loop failed to complete.", "impact_score": 1}

        for i in range(settings.REACT_MAX_ITERATIONS):
            response = await self.brain.call_ai_async(messages, model_tier="high")
            messages.append({"role": "assistant", "content": response})

            parsed = {}
            if "<analysis>" in response:
                parsed = parse_xml_tag(response, "analysis")
            else:
                try:
                    parsed = json.loads(response)
                except Exception:
                    json_match = re.search(r"\{.*\}", response, re.DOTALL)
                    parsed = json.loads(json_match.group()) if json_match else {}

            action = parsed.get("action", "")

            if "<analysis>" in response or action == "Finalize":
                raw_json = parsed.get("output", parsed) if action == "Finalize" else parsed
                final_result = {
                    "status": "success",
                    "analysis": str(raw_json.get("deep_analysis_text", "")),
                    "impact_score": float(raw_json.get("impact_score", 5)),
                    "raw_json": raw_json,
                }
                break

            elif action in ("Search", "Fetch", "Think"):
                messages.append({
                    "role": "user",
                    "content": f"[Tool result for step {i + 1}]: Processed."
                })

        return final_result

    async def run(self, news_id: int, db: AsyncSession) -> dict:
        notifier = DiscordNotifier()

        result = await db.execute(
            select(PendingNews).where(PendingNews.id == news_id)
        )
        news = result.scalar_one_or_none()
        if not news:
            logger.error(f"Stage 3: PendingNews id={news_id} not found.")
            return {"status": "error", "analysis": "Article not found.", "impact_score": 1}

        logger.info(f"Stage 3: Starting analysis on '{news.title[:60]}' [{news.url}]")
        content, is_valid, fetch_reason = await _fetch_full_content(news.url)

        if not is_valid:
            logger.warning(
                f"Stage 3: [INACCESSIBLE] {fetch_reason} — {news.url}"
            )
            news.status = "INACCESSIBLE"
            await db.commit()
            return {
                "status": "skipped",
                "reason": fetch_reason,
                "news_id": news_id,
                "url": news.url,
            }

        logger.info(f"Stage 3: Successfully fetched {len(content)} characters from {news.url}")

        filtered_signals = [{
            "title": news.title,
            "url": news.url,
            "source_domain": news.source_domain or "",
            "category": news.category or "OTHER",
            "content": content,
            "snippet": news.snippet or "",
        }]

        result_data = await self._run_react_loop(filtered_signals)

        if result_data.get("status") == "success":
            raw = result_data.get("raw_json", {})

            source_citations = [news.url]
            analysis_text = result_data.get("analysis", "")
            additional_urls = re.findall(r"https?://[^\s\)\]\>\"\']+", analysis_text)
            for u in additional_urls:
                u_clean = u.rstrip(".,;:!?")
                if u_clean not in source_citations:
                    source_citations.append(u_clean)
            source_citations = source_citations[:10]

            tech_trends_raw = raw.get("tech_trends", "")
            if isinstance(tech_trends_raw, list):
                tech_lines = []
                for t in tech_trends_raw:
                    if isinstance(t, dict):
                        trend = t.get("trend") or t.get("name") or ""
                        desc = t.get("description") or t.get("update") or t.get("details") or ""
                        if trend:
                            tech_lines.append(f"• **{trend}**: {desc}".strip(": "))
                technical_deep_dive_text = "\n".join(tech_lines) if tech_lines else ""
            elif isinstance(tech_trends_raw, str):
                technical_deep_dive_text = tech_trends_raw
            else:
                technical_deep_dive_text = ""

            emp_raw = raw.get("employment_status", "")
            if isinstance(emp_raw, dict):
                parts = []
                for key, val in emp_raw.items():
                    label = {
                        "status": "Trạng thái thị trường",
                        "market": "Thị trường",
                        "demand": "Nhu cầu tuyển dụng",
                        "details": "Chi tiết",
                    }.get(key, key.capitalize())
                    parts.append(f"**{label}:** {val}")
                vietnam_market_impact_text = "\n".join(parts)
            elif isinstance(emp_raw, str):
                vietnam_market_impact_text = emp_raw
            else:
                vietnam_market_impact_text = ""

            report = ResearchReport(
                pending_news_id=news.id,
                title=news.title,
                original_source=news.url,
                category=news.category,
                executive_summary=str(
                    raw.get("deep_analysis_text", result_data.get("analysis", ""))
                )[:2000],
                technical_deep_dive=technical_deep_dive_text or None,
                vietnam_market_impact=vietnam_market_impact_text or None,
                strategic_action_items=raw.get("job_details", {}).get("top_roles", []),
                impact_score=float(raw.get("impact_score", result_data.get("impact_score", 5))),
                sentiment=raw.get("sentiment", "NEUTRAL"),
                tags=[
                    t.get("trend") for t in raw.get("tech_trends", []) if isinstance(t, dict)
                ],
                source_citations=source_citations,
                content_accessible=True,
                raw_analysis={
                    **raw,
                    "source_citations": source_citations,
                    "content_length_fetched": len(content),
                    "fetch_method": "jina_reader",
                },
            )
            db.add(report)

            news.status = "PROCESSED"
            await db.commit()

            logger.info(
                f"Stage 3: Completed '{news.title[:60]}' — "
                f"score={report.impact_score} | {len(source_citations)} citations"
            )

            await notifier.send_strategic_report(
                title=report.title,
                url=report.original_source or "",
                executive_summary=report.executive_summary or "",
                vietnam_impact=report.vietnam_market_impact or "",
                action_items=report.strategic_action_items or [],
                source_citations=source_citations,
            )

        return result_data
