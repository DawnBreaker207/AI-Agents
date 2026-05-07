import logging

from ddgs import DDGS

logger = logging.getLogger(__name__)

def search_the_web(query: str):
    """Tìm kiếm web và trả về danh sách các kết quả dạng dictionary"""
    results = []
    try:
        with DDGS() as ddgs:
            # Lấy 5 kết quả tìm kiếm
            ddgs_gen = ddgs.text(query, max_results=5)
            for r in ddgs_gen:
                results.append({
                    "title": r.get('title', ''),
                    "body": r.get('body', ''),
                    "href": r.get('href', '')
                })
        return results
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm DuckDuckGo: {e}")
        return []
