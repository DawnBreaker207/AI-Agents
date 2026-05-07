import logging

from app.core.brain import BrainService

logger = logging.getLogger(__name__)


class ChatEngine:
    """
    Thay vì gọi là AgentEngine (dễ nhầm với Maestro Pipeline),
    ta đổi tên thành ChatEngine. Nhiệm vụ duy nhất của nó là:
    Hỏi đáp (Q&A) dựa trên các Báo cáo Chiến lược đã được lưu trong Database (RAG).
    """

    def __init__(self):
        self.brain = BrainService()

    async def run_analyst(self, user_prompt: str, context_reports: list) -> str:
        # 1. Trích xuất tri thức từ Database để làm ngữ cảnh (Context)
        if not context_reports:
            return "Hiện tại hệ thống chưa có dữ liệu báo cáo nào về chủ đề này. Hãy chạy lệnh nghiên cứu trước."

        context_text = "\n---\n".join([
            f"Tiêu đề: {r.title}\n Tóm tắt báo cáo: {r.content}\n Điểm ảnh hưởng (Impact): {r.impact_score}/10"
            for r in context_reports
        ])

        # 2. Xây dựng Prompt ép AI chỉ trả lời dựa trên Context
        system_prompt = """
        Bạn là Chuyên gia Phân tích Chiến lược Công nghệ cấp cao.
        Nhiệm vụ của bạn là trả lời câu hỏi của người dùng DỰA VÀO KHO DỮ LIỆU ĐƯỢC CUNG CẤP DƯỚI ĐÂY.

        NGUYÊN TẮC:
        1. Tuyệt đối không bịa đặt thông tin (No Hallucination). Nếu dữ liệu không có câu trả lời, hãy nói rõ: "Dữ liệu hiện tại chưa đề cập đến vấn đề này".
        2. Luôn trích dẫn tên "Tiêu đề" bài báo cáo khi đưa ra dẫn chứng.
        3. Văn phong: Chuyên nghiệp, ngắn gọn, súc tích (Dùng Markdown).
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"KHO DỮ LIỆU BÁO CÁO TỪ HỆ THỐNG TSI:\n{context_text}"},
            {"role": "user", "content": user_prompt}
        ]

        # 3. Gọi High-reasoning Model (Claude 3.5 / GPT-4o) để trả lời user
        # Ở bước giao tiếp trực tiếp với User, luôn dùng model thông minh nhất.
        try:
            logger.info("ChatEngine đang phân tích câu hỏi của user...")
            answer = self.brain.call_ai(messages, model_tier="high")
            return answer
        except Exception as e:
            logger.error(f"Lỗi khi chạy ChatEngine: {e}")
            return "Hệ thống AI đang bận hoặc gặp sự cố, vui lòng thử lại sau."
