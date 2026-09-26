"""HEAD-check dùng chung: Scout (RSS) và Job Search đều dùng để loại link chết."""
import logging
from urllib.parse import urlparse

import httpx

from app.utils.helpers import extract_domain, is_homepage_path

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
_HEAD_TIMEOUT = 10


async def is_article_accessible(url: str, client: httpx.AsyncClient) -> tuple[bool, str]:
    """Kiểm tra URL có trỏ đến bài viết thực không bằng HEAD request.

    Returns: (True, "") nếu OK, hoặc (False, reason) nếu không dùng được.
    """
    try:
        resp = await client.head(
            url,
            headers=_HEADERS,
            follow_redirects=True,
            timeout=_HEAD_TIMEOUT,
        )
        # Site không hỗ trợ HEAD (405/501) → thử GET nhẹ thay vì loại luôn
        if resp.status_code in (405, 501):
            try:
                resp = await client.get(
                    url,
                    headers=_HEADERS,
                    follow_redirects=True,
                    timeout=_HEAD_TIMEOUT,
                )
            except Exception as e:
                return False, f"GET fallback lỗi: {type(e).__name__}"
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
