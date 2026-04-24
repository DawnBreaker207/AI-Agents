from bs4 import BeautifulSoup
import requests


def get_web_content(url: str):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',

        }
        res = requests.get(url, timeout=10, headers=headers, verify=true)
        res.raise_for_status()
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        for s in soup(["script", "style", "nav", "footer", "header", "aside"]): s.decompose()
        content = soup.get_text(separator=' ').strip()
        content = ' '.join(content.split())
        return content[:400]

    except Exception as e:
        return f"Lỗi truy cập web: {str(e)}"
