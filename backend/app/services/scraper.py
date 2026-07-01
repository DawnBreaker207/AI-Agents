import logging
import re
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

logger = logging.getLogger(__name__)


def clean_html_content(html_raw: str) -> str:
    if not html_raw:
        return ""
    soup = BeautifulSoup(html_raw, 'html.parser')
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        element.decompose()
    text = soup.get_text(separator=' ')
    clean_text = re.sub(r'\s+', ' ', text).strip()
    return clean_text


async def get_web_content(url_input: str | dict) -> str:
    url = ""
    if isinstance(url_input, dict):
        url = url_input.get("url") or url_input.get("args") or list(url_input.values())[0]
    else:
        url = str(url_input)

    url = url.strip().strip("'\"`")

    if not url.startswith("http"):
        return f"Error: Invalid URL (must start with http or https): {url}"

    # Encode URL to handle special characters safely
    jina_url = f"https://r.jina.ai/{quote(url, safe='')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 TSI-Agent/2026',
        'X-Return-Format': 'text'
    }

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            res = await client.get(jina_url, headers=headers)
            res.raise_for_status()

        content = res.text

        if not content.strip():
            return f"Observation: Jina could not extract content from {url}."

        max_len = getattr(settings, "WEB_CONTENT_MAX_LENGTH", 6000)
        return content[:max_len]

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 403:
            return f"Observation: Access Denied (403). Website blocks bots: {url}"
        return f"Observation: HTTP {status_code} error while accessing {url}."

    except httpx.ConnectError:
        return f"Observation: Failed to connect to {url}."

    except httpx.RequestError as e:
        return f"Observation: Network error: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error processing URL {url}: {e}")
        return f"Observation: System error processing {url}."
