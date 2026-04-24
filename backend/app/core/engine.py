import json
from .brain import BrainService
from app.tools import TOOL_REGISTRY


class AgentEngine:
    def __init__(self):
        self.brain = BrainService()

    def run(self, user_prompt):
        messages = [
            {
                "role": "system",
                "content": f"""Bạn là Trợ lý AI chuyên nghiệp.
                     Công cụ: {list(TOOL_REGISTRY.keys())}.

                     QUY ĐỊNH TRẢ VỀ JSON:
                     Nếu status là 'continue', 'answer' có thể là chuỗi trống.
                     Nếu status là 'finished', 'answer' PHẢI là một JSON Object có cấu trúc:
                     {{
                         "title": "Tiêu đề báo cáo",
                         "key_points": ["ý 1", "ý 2", "ý 3"],
                         "sentiment": "Tích cực/Tiêu cực/Trung lập",
                         "token_usage_saved": 0
                     }}

                     Mẫu JSON trả về:
                     {{
                         "thought": "suy nghĩ",
                         "tool": "tên_tool_hoặc_null",
                         "args": "tham số",
                         "status": "continue_hoặc_finished",
                         "answer": {{ ... cấu trúc như trên ... }}
                     }}"""
            },
            {"role": "user", "content": user_prompt}
        ]

        for i in range(5):
            raw_res = self.brain.call_ai(messages)

            clean_res = raw_res.replace("```json", "").replace("```", "").strip()
            decision = json.loads(clean_res)

            print(f"--- Bước {i + 1}: AI đang nghĩ: {decision['thought']}")

            # 2. Nếu xong việc thì thoát
            if decision['status'] == 'finished':
                print(f"[Bước {i + 1}] ✅ Hoàn thành nhiệm vụ!")
                return decision['answer']
            tool_name = decision.get('tool')
            if tool_name in TOOL_REGISTRY:
                print(f"[Bước {i + 1}] 🛠️  Hành động: Đang sử dụng công cụ [{tool_name}]...")
                obs = TOOL_REGISTRY[decision['tool']]['func'](decision['args'])
                messages.append({"role": "assistant", "content": clean_res})
                messages.append({"role": "system", "content": f"Observation: {obs}"})
            else:
                print(f"[Bước {i + 1}] ⚠️ Cảnh báo: AI chọn tool không tồn tại hoặc không chọn tool.")

        return "Agent không thể hoàn thành nhiệm vụ sau 5 bước."
