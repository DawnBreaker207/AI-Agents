import inspect
import json
import logging
import re

from app.tools import TOOL_REGISTRY
from .brain import BrainService
from .prompt import FINAL_SUMMARY_PROMPT, FORCE_FINISH_PROMPT, RESEARCH_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class AgentEngine:
    def __init__(self):
        self.brain = BrainService()
        self.max_iterations = 15

    async def _final_summary(self, messages):
        messages.append({"role": "user", "content": FINAL_SUMMARY_PROMPT})

        final_res = self.brain.call_ai(messages)
        try:
            import re
            json_match = re.search(r'\{.*\}', final_res, re.DOTALL)
            clean_res = json_match.group(0) if json_match else final_res
            data = json.loads(clean_res)
            return data.get('answer') if 'answer' in data else data
        except:
            return {
                "summary": "Không thể tổng hợp báo cáo chi tiết, nhưng đã hoàn thành tìm kiếm.",
                "key_points": [], "sentiment": "Trung tính", "sources": [], "categories": [], "regions": []
            }

    async def run(self, user_prompt):
        tool_text = "\n".join([f"- {name}: {info['description']}" for name, info in TOOL_REGISTRY.items()])
        steps_text = "1. Tìm kiếm -> 2. Đọc -> 3. Tổng hợp"
        system_prompt = RESEARCH_SYSTEM_PROMPT.format(
            tool_descriptions=tool_text,
            process_steps=steps_text
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        for i in range(self.max_iterations):

            if i >= self.max_iterations - 2:
                force_prompt = FORCE_FINISH_PROMPT
                messages.append({"role": "system",
                                 "content": force_prompt})
            raw_res = self.brain.call_ai(messages)

            try:
                json_match = re.search(r'\{.*\}', raw_res, re.DOTALL)
                clean_res = json_match.group(0) if json_match else raw_res
                decision = json.loads(clean_res)
            except json.JSONDecodeError:
                print(f"[Bước {i + 1}] ❌ Lỗi: AI trả về JSON không hợp lệ. Đang thử lại.")
                messages.append({"role": "system",
                                 "content": "Lỗi: Phản hồi của bạn không phải là một JSON hợp lệ. Vui lòng kiểm tra lại cấu trúc."})
                continue

            print(f"--- Bước {i + 1}: AI đang nghĩ: {decision.get('thought', 'Không có suy nghĩ')}")

            if decision.get('status') == 'finished' or i == self.max_iterations - 1:
                print(f"[Bước {i + 1}] ✅ Hoàn thành nhiệm vụ!")
                if not decision.get('answer') or i == self.max_iterations - 1:
                    return await self._final_summary(messages)
                return decision.get('answer')

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

        return {"summary": f"Agent không thể hoàn thành nhiệm vụ sau {self.max_iterations} bước.", "key_points": [],
                "sentiment": "Không xác định", "sources": [], "categories": [], "regions": []}
