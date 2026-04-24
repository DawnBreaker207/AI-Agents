import logging

import httpx
from bs4 import BeautifulSoup

from config import settings


async def get_web_content(url_input: str | dict):
    url = ""
    if isinstance(url_input, dict):

        url = url_input.get("url") or url_input.get("args") or list(url_input.values())[0]
    else:
        url = str(url_input)

    url = url.strip().strip("'\"`")

    if not url.startswith("http"):
        return f"Error: Invalid URL (must start with http or https): {url}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Return-Format': 'text'
    }
    jina_url = f"https://r.jina.ai/{url}"
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            res = await client.get(jina_url, headers=headers, timeout=15, follow_redirects=True)
            res.raise_for_status()

        content = res.text

        # Kiểm tra nếu nội dung rỗng
        if not content.strip():
            return f"Error: Jina could not extract content from {url}"

        return content[:settings.WEB_CONTENT_MAX_LENGTH]

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 403:
            return f"Error: Access Denied (403 Forbidden). Website blocks automated tools: {url}"
        return f"Error: HTTP {status_code} error while accessing {url}."

    except httpx.ConnectError:
        return f"Error: Failed to connect or SSL certificate issue for {url}."

    except httpx.RequestError as e:
        return f"Error: A network error occurred: {str(e)}"

    except Exception as e:
        logging.error(f"An unexpected error occurred while processing URL {url}: {e}")
        return f"Error: An unexpected error occurred while processing {url}. {str(e)}"
