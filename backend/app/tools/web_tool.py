import requests
from bs4 import BeautifulSoup


def get_web_content(url_input: str):
    url = ""
    if isinstance(url, dict):
        url = url_input.get("url") or url_input.get("args") or list(url_input.values())[0]
    else:
        url = str(url_input)

    url = url.strip().strip("'").strip('"')

    if not url.startswith("http"):
        return f"Lỗi: URL không hợp lệ (thiếu http/https): {url}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',

        }
        res = requests.get(
            url,
            timeout=15,
            headers=headers,
            verify=False
        )

        res.raise_for_status()
        res.encoding = 'utf-8'

        soup = BeautifulSoup(res.text, "html.parser")

        for s in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            s.decompose()

        content = soup.get_text(separator=' ').strip()
        content = ' '.join(content.split())

        return content[:4000]

    except Exception as e:
        return f"Lỗi truy cập web: {str(e)}"
