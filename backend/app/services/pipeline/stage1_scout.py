import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.helpers import normalize_url, extract_domain, clean_html_snippet, is_homepage_path
from app.models.source import SourceList
from app.models.news import PendingNews
from app.services.notify import DiscordNotifier
from app.core.config import settings

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
_HEAD_TIMEOUT = 10


async def _is_article_accessible(url: str, client: httpx.AsyncClient) -> tuple[bool, str]:
    try:
        resp = await client.head(
            url,
            headers=_HEADERS,
            follow_redirects=True,
            timeout=_HEAD_TIMEOUT,
        )
        if resp.status_code >= 400:
            return False, f"HTTP {resp.status_code}"

        final_url = str(resp.url)
        final_parsed = urlparse(final_url)

        if is_homepage_path(final_parsed.path):
            return False, f"Redirected to homepage: {final_url}"

        original_domain = extract_domain(url)
        final_domain = extract_domain(final_url)
        if final_domain != original_domain:
            orig_root = original_domain.split(".")[-2] if "." in original_domain else original_domain
            final_root = final_domain.split(".")[-2] if "." in final_domain else final_domain
            if orig_root != final_root:
                return False, f"Redirected to different domain: {final_domain}"

        return True, ""

    except httpx.TimeoutException:
        return False, "Timeout"
    except httpx.TooManyRedirects:
        return False, "Too many redirects"
    except Exception as e:
        return False, f"Connection error: {type(e).__name__}"


class ScoutStage:

    async def run(self, db: AsyncSession, time_window_hours: int | None = None) -> int:
        notifier = DiscordNotifier()
        result = await db.execute(
            select(SourceList).where(SourceList.is_active == True)
        )
        sources = result.scalars().all()
        new_count = 0

        cutoff_time = datetime.now(timezone.utc) - timedelta(
            hours=time_window_hours or settings.SCOUT_TIME_WINDOW_HOURS
        )

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
                        db.add(news)
                        await db.flush()

                        new_count += 1
                        source_new_count += 1

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
        if new_count > 0:
            from app.core.events import news_broadcaster
            news_broadcaster.broadcast({"type": "new_news"})
        logger.info(f"Scout completed: {new_count} new articles (all verified accessible).")
        return new_count
