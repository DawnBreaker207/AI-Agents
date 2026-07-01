import logging

from app.core.brain import BrainService
from app.prompts.analyst import CHAT_ANALYST_PROMPT

logger = logging.getLogger(__name__)


class ChatEngine:

    def __init__(self):
        self.brain = BrainService()

    async def run_analyst(self, user_prompt: str, context_reports: list) -> str:
        if not context_reports:
            return "Hiện tại hệ thống chưa có dữ liệu báo cáo nào về chủ đề này. Hãy chạy lệnh nghiên cứu trước."

        context_text = "\n---\n".join([
            f"Tiêu đề: {r.title}\n Tóm tắt báo cáo: {r.executive_summary or r.technical_deep_dive}\n URL Nguồn: {r.original_source}\n Điểm ảnh hưởng (Impact): {r.impact_score}/10"
            for r in context_reports
        ])

        messages = [
            {"role": "system", "content": CHAT_ANALYST_PROMPT},
            {"role": "system", "content": f"KHO DỮ LIỆU BÁO CÁO TỪ HỆ THỐNG TSI:\n{context_text}"},
            {"role": "user", "content": user_prompt}
        ]

        try:
            logger.info("ChatEngine đang phân tích câu hỏi của user...")
            answer = await self.brain.call_ai_async(messages, model_tier="high")
            return answer
        except Exception as e:
            logger.error(f"Lỗi khi chạy ChatEngine: {e}")
            return "Hệ thống AI đang bận hoặc gặp sự cố, vui lòng thử lại sau."
