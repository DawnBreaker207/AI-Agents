import json
import inspect
import logging
from .brain import BrainService
from app.tools import TOOL_REGISTRY

logger = logging.getLogger(__name__)


class AgentEngine:
    def __init__(self):
        self.brain = BrainService()
        self.max_iterations = 15

    async def run(self, user_prompt):
        tool_descriptions = "\n".join([f"- {name}: {info['description']}" for name, info in TOOL_REGISTRY.items()])

        system_prompt = f"""Bạn là một Agent AI chuyên phân tích thị trường công nghệ, với nhiệm vụ tìm kiếm và tổng hợp thông tin để trả lời câu hỏi của người dùng.

QUY TRÌNH LÀM VIỆC ĐỀ XUẤT:
1.  **Suy nghĩ**: Dựa vào yêu cầu của người dùng, hãy xác định những từ khóa tìm kiếm phù hợp.
2.  **Hành động (search_the_web)**: Sử dụng công cụ `search_the_web` với những từ khóa đã xác định để tìm các bài báo hoặc nguồn tin tức liên quan.
3.  **Suy nghĩ**: Xem xét kết quả tìm kiếm. Chọn ra 2-3 URL hứa hẹn nhất để đọc chi tiết.
4.  **Hành động (read_web_content)**: Sử dụng công cụ `read_web_content` lần lượt với từng URL đã chọn để lấy nội dung chi tiết.
5.  **Suy nghĩ và Hoàn thành**: Sau khi đã có đủ thông tin, tổng hợp lại thành một báo cáo hoàn chỉnh và kết thúc nhiệm vụ.

CÁC CÔNG CỤ BẠN CÓ:
{tool_descriptions}

QUY ĐỊNH TRẢ VỀ JSON:
- Luôn trả về một JSON object.
- Nếu `status` là 'continue', `answer` có thể là một chuỗi trống.
- Nếu `status` là 'finished', `answer` PHẢI là một JSON Object có cấu trúc sau:
    {{
        "summary": "Một đoạn tóm tắt chính, trả lời trực tiếp câu hỏi của người dùng.",
        "key_points": ["Điểm chính 1", "Điểm chính 2", "Điểm chính 3"],
        "sentiment": "Tích cực/Tiêu cực/Trung lập (Dựa trên các tin tức tìm được)",
        "sources": ["url_nguon_1", "url_nguon_2"],
        "categories: ["Công nghệ"],
        "regions": ["Toàn cầu]
    }}

MẪU JSON CHO MỖI BƯỚC:
{{
    "thought": "Suy nghĩ của bạn về bước tiếp theo.",
    "tool": "tên_công_cụ_sẽ_dùng (hoặc null nếu muốn kết thúc)",
    "args": "tham_số_cho_công_cụ",
    "status": "continue (nếu cần thêm bước) hoặc finished (nếu đã đủ thông tin để trả lời)",
    "answer": {{ ... cấu trúc như trên nếu status là finished ... }}
}}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        for i in range(self.max_iterations):
            raw_res = self.brain.call_ai(messages)

            try:
                clean_res = raw_res.replace("```json", "").replace("```", "").strip()
                decision = json.loads(clean_res)
            except json.JSONDecodeError:
                print(f"[Bước {i + 1}] ❌ Lỗi: AI trả về JSON không hợp lệ. Đang thử lại.")
                messages.append({"role": "system",
                                 "content": "Lỗi: Phản hồi của bạn không phải là một JSON hợp lệ. Vui lòng kiểm tra lại cấu trúc."})
                continue

            print(f"--- Bước {i + 1}: AI đang nghĩ: {decision.get('thought', 'Không có suy nghĩ')}")

            if decision.get('status') == 'finished':
                print(f"[Bước {i + 1}] ✅ Hoàn thành nhiệm vụ!")
                return decision.get('answer', {"summary": "Không có câu trả lời."})

            tool_name = decision.get('tool')
            if tool_name in TOOL_REGISTRY:
                print(f"[Bước {i + 1}] 🛠️  Hành động: Đang sử dụng công cụ [{tool_name}]...")
                tool_func = TOOL_REGISTRY[tool_name]['func']
                tool_args = decision.get('args', '')

                if not isinstance(tool_args, str):
                    tool_args = str(tool_args)

                if inspect.iscoroutinefunction(tool_func):
                    obs = await tool_func(tool_args)
                else:
                    obs = tool_func(tool_args)

                messages.append({"role": "assistant", "content": clean_res})
                obs_summary = f"Kết quả từ công cụ {tool_name}: {obs[:2000]}..." if len(
                    obs) > 2000 else f"Kết quả từ công cụ {tool_name}: {obs}"
                messages.append({"role": "system", "content": obs_summary})
            else:
                print(f"[Bước {i + 1}] ⚠️ Cảnh báo: AI không chọn công cụ hợp lệ. Yêu cầu AI suy nghĩ lại.")
                messages.append({"role": "system",
                                 "content": "Bạn chưa chọn một công cụ hợp lệ. Hãy suy nghĩ lại và chọn một hành động từ danh sách công cụ của bạn, hoặc kết thúc nhiệm vụ nếu bạn đã có đủ thông tin."})

        return {"summary": "Agent không thể hoàn thành nhiệm vụ sau 7 bước.", "key_points": [],
                "sentiment": "Không xác định", "sources": [], "categories": [], "regions": []}
