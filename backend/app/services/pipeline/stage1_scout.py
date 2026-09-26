import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.helpers import normalize_url, extract_domain, clean_html_snippet
from app.utils.link_check import is_article_accessible as _is_article_accessible
from app.models.source import SourceList
from app.models.news import PendingNews
from app.models.category import TopicWhitelist
from app.services.notify import DiscordNotifier
from app.core.config import settings
from app.services.pipeline.stage2_filter import CRITICAL_KEYWORDS, LAYOFF_KEYWORDS

logger = logging.getLogger(__name__)

_HEAD_TIMEOUT = 10


_LARGE_NUMBER_PATTERN = re.compile(
    r'(\d{1,3}[,.]?\d{3}\+?)\s*(nhân viên|employees|jobs|workers|positions|staff|người)',
    re.IGNORECASE
)


_BREAKING_DEDUP_HOURS = 24
_FAST_LANE_CONCURRENCY = 3


def _is_breaking_news(
    title: str, snippet: str, whitelist: list[TopicWhitelist],
) -> tuple[bool, str, str]:
    """Rule-based fast filter: layoff/critical keyword + số liệu lớn hoặc
    công ty khớp TopicWhitelist có force_keep=True (quản lý qua UI Sources).

    Returns: (is_breaking, reason, matched_company).
    """
    combined = f"{title or ''} {(snippet or '')}".strip()
    lowered = combined.lower()

    has_urgent_kw = any(
        kw.lower() in lowered for kw in CRITICAL_KEYWORDS + LAYOFF_KEYWORDS
    )
    if not has_urgent_kw:
        return False, "", ""

    large_match = _LARGE_NUMBER_PATTERN.search(combined)
    if large_match:
        return True, f"urgent keyword + large number '{large_match.group(0).strip()}'", ""

    for wl in whitelist:
        topic = str(wl.topic or "")
        if topic and bool(wl.force_keep) and topic.lower() in lowered:
            return True, f"force_keep watchlist '{topic}' + urgent keyword", topic

    return False, "", ""


async def _is_duplicate_breaking(
    db: AsyncSession, company: str, hours: int = _BREAKING_DEDUP_HOURS,
) -> bool:
    """Chống spam Discord: cùng company + LAYOFF đã có KEEP_URGENT trong X giờ gần đây?"""
    if not company:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(
        select(PendingNews)
        .where(PendingNews.status == "KEEP_URGENT")
        .where(PendingNews.category == "LAYOFF")
        .where(PendingNews.published_at != None)  # noqa: E711
        .where(PendingNews.published_at >= cutoff)
        .limit(50)
    )
    for row in result.scalars().all():
        haystack = f"{row.title or ''} {row.snippet or ''}".lower()
        if company.lower() in haystack:
            return True
    return False


async def _run_fast_lane_stage3(news_id: int, title: str):
    """Chạy Stage 3 cho 1 tin breaking trên session riêng (an toàn cho gather)."""
    from app.database import AsyncSessionLocal
    from app.services.pipeline.stage3_deep import DeepAnalysisStage
    try:
        async with AsyncSessionLocal() as db:
            await DeepAnalysisStage().run(news_id, db)
    except Exception as e:
        logger.error(f"Fast-lane Stage 3 failed [news_id={news_id}]: {e}")


class ScoutStage:

    async def run(self, db: AsyncSession, time_window_hours: int | None = None,
                source_filter: str | None = None) -> int:
        notifier = DiscordNotifier()
        query = select(SourceList).where(SourceList.is_active == True)
        if source_filter:
            query = query.where(SourceList.scan_priority == source_filter)
        result = await db.execute(query)
        sources = result.scalars().all()
        new_count = 0

        cutoff_time = datetime.now(timezone.utc) - timedelta(
            hours=time_window_hours or settings.SCOUT_TIME_WINDOW_HOURS
        )

        wl_result = await db.execute(
            select(TopicWhitelist).where(TopicWhitelist.is_active == True)
        )
        whitelist = list(wl_result.scalars().all())
        breaking_ids: list[tuple[int, str]] = []  # (news_id, title) — chạy Stage 3 sau loop

        async with httpx.AsyncClient(timeout=_HEAD_TIMEOUT) as client:
            for source in sources:
                try:
                    feed = feedparser.parse(source.url)
                    feed_base_url = feed.feed.get("link", "") or source.url

                    total_entries = len(feed.entries)
                    logger.info(
                        f"Scout: Source '{source.name}' — {total_entries} entries. "
                        f"Base URL: {feed_base_url}"
                    )

                    source_new_count = 0
                    source_skip_invalid = 0
                    source_skip_old = 0
                    source_skip_dup = 0
                    source_skip_dead = 0

                    for entry in feed.entries:
                        raw_url = entry.get("link", "").strip()

                        normalized_url = normalize_url(raw_url, feed_base_url)
                        if not normalized_url:
                            source_skip_invalid += 1
                            continue

                        source_domain = extract_domain(normalized_url)

                        published = None
                        if hasattr(entry, "published_parsed") and entry.published_parsed:
                            pub_tuple = entry.published_parsed
                            try:
                                published = datetime(
                                    pub_tuple.tm_year, pub_tuple.tm_mon, pub_tuple.tm_mday,
                                    pub_tuple.tm_hour, pub_tuple.tm_min, pub_tuple.tm_sec,
                                    tzinfo=timezone.utc,
                                )
                                if published < cutoff_time:
                                    source_skip_old += 1
                                    continue
                            except (ValueError, OverflowError):
                                published = None

                        exists = await db.execute(
                            select(PendingNews).where(PendingNews.url == normalized_url)
                        )
                        if exists.scalar_one_or_none():
                            source_skip_dup += 1
                            continue

                        accessible, reason = await _is_article_accessible(normalized_url, client)
                        if not accessible:
                            logger.info(
                                f"  [SKIP-DEAD] '{entry.get('title', 'No title')[:60]}' "
                                f"— {reason} — {normalized_url}"
                            )
                            source_skip_dead += 1
                            continue

                        news = PendingNews(
                            title=entry.get("title", "No Title")[:500],
                            snippet=clean_html_snippet(entry.get("summary", "")),
                            url=normalized_url,
                            source_domain=source_domain,
                            published_at=published,
                            status="PENDING",
                        )
                        is_breaking, breaking_reason, matched_co = _is_breaking_news(
                            news.title, news.snippet or "", whitelist
                        )
                        if is_breaking:
                            if matched_co and await _is_duplicate_breaking(db, matched_co):
                                logger.info(
                                    f"  [SKIP-DUP-BREAKING] '{news.title[:60]}' — "
                                    f"sự kiện '{matched_co}' đã có alert trong "
                                    f"{_BREAKING_DEDUP_HOURS}h qua"
                                )
                                is_breaking = False
                            else:
                                news.status = "KEEP_URGENT"
                                news.category = "LAYOFF"
                        db.add(news)
                        await db.flush()

                        new_count += 1
                        source_new_count += 1

                        if is_breaking:
                            logger.warning(
                                f"🚨 BREAKING: {news.title[:80]} — {breaking_reason} "
                                f"— Stage 3 triggered"
                            )
                            breaking_ids.append((news.id, news.title))

                    # Dead-link health check
                    relevant = total_entries - source_skip_old  # chỉ tính entries trong time window
                    total_issues = source_skip_dead + source_skip_invalid
                    if relevant > 0 and (total_issues / relevant) > 0.5:
                        source.consecutive_fails = (source.consecutive_fails or 0) + 1
                        source.last_error = (
                            f"{total_issues}/{relevant} entries dead/invalid "
                            f"(run {source.consecutive_fails})"
                        )
                        logger.warning(
                            f"  ⚠ '{source.name}': {total_issues}/{relevant} entries dead — "
                            f"consecutive_fails={source.consecutive_fails}"
                        )
                    elif total_entries == 0:
                        source.consecutive_fails = (source.consecutive_fails or 0) + 1
                        source.last_error = f"Feed returned 0 entries (run {source.consecutive_fails})"
                        logger.warning(
                            f"  ⚠ '{source.name}': feed empty — "
                            f"consecutive_fails={source.consecutive_fails}"
                        )
                    else:
                        if source.consecutive_fails and source.consecutive_fails > 0:
                            logger.info(f"  ✓ '{source.name}': recovered, resetting fail counter")
                        source.consecutive_fails = 0
                        source.last_error = ""

                    # Auto-disable after 3 consecutive bad runs
                    if (source.consecutive_fails or 0) >= 3:
                        source.is_active = False
                        source.disabled_at = datetime.now(timezone.utc)
                        logger.warning(
                            f"  🔴 Auto-disabled '{source.name}' after "
                            f"{source.consecutive_fails} consecutive failures. "
                            f"Last error: {source.last_error}"
                        )

                    logger.info(
                        f"  → '{source.name}': "
                        f"{source_new_count} new | "
                        f"{source_skip_dead} dead/redirected | "
                        f"{source_skip_invalid} invalid URL | "
                        f"{source_skip_dup} duplicates | "
                        f"{source_skip_old} old"
                    )

                except Exception as e:
                    error_msg = f"{type(e).__name__}: {e}"
                    source.consecutive_fails = (source.consecutive_fails or 0) + 1
                    source.last_error = error_msg
                    if (source.consecutive_fails or 0) >= 3:
                        source.is_active = False
                        source.disabled_at = datetime.now(timezone.utc)
                        logger.warning(
                            f"  🔴 Auto-disabled '{source.name}' after "
                            f"{source.consecutive_fails} consecutive failures: {error_msg}"
                        )
                    else:
                        logger.error(f"Scout error [{source.name}]: {error_msg}")

        await db.commit()

        # Fast lane: chạy Stage 3 song song cho tin breaking (không block Scout,
        # mỗi tin 1 session riêng + try/except riêng)
        if breaking_ids:
            sem = asyncio.Semaphore(_FAST_LANE_CONCURRENCY)

            async def _guarded(news_id: int, title: str):
                async with sem:
                    await _run_fast_lane_stage3(news_id, title)

            await asyncio.gather(*[_guarded(nid, t) for nid, t in breaking_ids])
            logger.info(f"Scout fast lane: {len(breaking_ids)} breaking news → Stage 3.")

        if new_count > 0:
            from app.core.events import news_broadcaster
            news_broadcaster.broadcast({"type": "new_news"})
        logger.info(f"Scout completed: {new_count} new articles (all verified accessible).")
        return new_count
