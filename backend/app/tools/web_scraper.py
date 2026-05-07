import logging
import re
import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

logger = logging.getLogger(__name__)
def clean_html_content(html_raw: str) -> str:
    """
    Làm sạch mã HTML rác (Chỉ dùng khi cào raw HTML).
    Áp dụng triết lý "Lazy AI" - dùng Regex và BS4 thay vì AI.
    """
    if not html_raw:
        return ""

    # 1. Parse HTML
    soup = BeautifulSoup(html_raw, 'html.parser')

    # 2. Loại bỏ các tag rác
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        element.decompose()

    # 3. Lấy text
    text = soup.get_text(separator=' ')

    # 4. Xóa khoảng trắng, dấu tab, dòng trống dư thừa bằng Regex
    clean_text = re.sub(r'\s+', ' ', text).strip()

    return clean_text


async def get_web_content(url_input: str | dict) -> str:
    """
    Cào nội dung Web sâu bằng Jina Reader API.
    Lưu ý: Jina Reader đã tự động trả về định dạng Markdown/Text sạch.
    """
    url = ""
    if isinstance(url_input, dict):
        # Trích xuất URL nếu đầu vào là 1 dictionary (Thường do AI sinh ra)
        url = url_input.get("url") or url_input.get("args") or list(url_input.values())[0]
    else:
        url = str(url_input)

    url = url.strip().strip("'\"`")

    if not url.startswith("http"):
        return f"Error: Invalid URL (must start with http or https): {url}"

    # Cấu hình Jina AI Reader
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        'User-Agent': 'Mozilla/5.0 TSI-Agent/2026',
        'X-Return-Format': 'text'  # Yêu cầu Jina trả về text sạch
    }

    try:
        # Sử dụng httpx.AsyncClient để không block luồng của FastAPI
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            res = await client.get(jina_url, headers=headers)
            res.raise_for_status()

        content = res.text

        if not content.strip():
            return f"Observation: Jina could not extract content from {url}. Maybe it's blocked."

        # Cắt độ dài để tránh tràn Context Window của LLM
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