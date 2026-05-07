import re
import logging
from app.tools.web_search import search_the_web
from app.tools.web_scraper import get_web_content, clean_html_content

logger = logging.getLogger(__name__)

class ScoutStage:
    def __init__(self):
        # Các từ khóa kích hoạt "Bẫy tin tức"
        self.keywords = ["layoff", "hiring", "nvidia", "oracle", "genai", "sa thải", "tuyển dụng", "lương", "salary"]

    def is_triggered(self, text: str) -> bool:
        """Kiểm tra bẫy tin tức"""
        if not text: return False
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.keywords)

    async def run(self, topic: str) -> list:
        logger.info(f"Stage 1: Đang tìm kiếm thông tin cho chủ đề: {topic}")

        # Gọi tool search (Bây giờ trả về list các dict)
        search_results = search_the_web(topic)

        if not isinstance(search_results, list):
            logger.warning("Kết quả tìm kiếm không hợp lệ.")
            return []

        valid_data = []
        for item in search_results:
            # Kết hợp title và body để kiểm tra bẫy tin tức
            combined_text = item.get('title', '') + " " + item.get('body', '')

            if self.is_triggered(combined_text):
                logger.info(f"🎯 Kích hoạt bẫy tin tức: {item.get('title')}")

                # Cào nội dung chi tiết từ URL
                raw_content = await get_web_content(item.get('href'))

                # Làm sạch nội dung (Lazy AI)
                clean_text = clean_html_content(raw_content)

                valid_data.append({
                    "title": item.get('title'),
                    "url": item.get('href'),
                    "content": clean_text[:4000]
                })

        logger.info(f"Stage 1 hoàn tất: Tìm thấy {len(valid_data)} tín hiệu phù hợp.")
        return valid_data
