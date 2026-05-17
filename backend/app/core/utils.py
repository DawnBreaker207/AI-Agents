import json
import logging
import re

logger = logging.getLogger(__name__)


def parse_json_column(data, default_value=None):
    if data is None:
        return default_value if default_value is not None else []
    if isinstance(data, (list, dict)):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return default_value if default_value is not None else []
    return default_value


def parse_xml_tag(text: str, tag: str) -> dict:
    """
    Trích xuất nội dung giữa các thẻ (ví dụ: <analysis>...</analysis>)
    và chuyển đổi sang Dictionary.
    """
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            logger.error(f"Lỗi parse JSON từ tag <{tag}>")
    return {}


def parse_analysis_tag(text: str) -> dict:
    """Trích xuất và parse JSON từ thẻ <analysis>"""
    pattern = r"<analysis>(.*?)</analysis>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            logger.error("Không thể parse JSON từ Stage 3")
    return {}


def normalize_url(raw_url: str, feed_base_url: str = "") -> str | None:
    """Normalize RSS entry URLs to a single canonical form."""
    from urllib.parse import urlparse, urljoin, urlunparse
    if not raw_url:
        return None
    url = raw_url.strip()
    if feed_base_url and not url.startswith(("http://", "https://")):
        url = urljoin(feed_base_url, url)
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip("/") or "/",
        parsed.params,
        parsed.query,
        "",  # Strip fragment identifier (#) to avoid duplicate records
    ))
    return normalized


def extract_domain(normalized_url: str) -> str:
    """Extract domain from a normalized URL, always stripping 'www.' prefix."""
    from urllib.parse import urlparse
    netloc = urlparse(normalized_url).netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def clean_html_snippet(raw_snippet: str) -> str:
    """Strip HTML tags from RSS content to obtain plain-text snippets."""
    if not raw_snippet:
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_snippet)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:1000]


def is_homepage_path(path: str) -> bool:
    """Check if the given path indicates a homepage or index page."""
    normalized_path = path.rstrip("/").lower()
    return normalized_path in ("", "/", "/index", "/index.html", "/home", "/index.htm")
