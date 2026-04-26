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

    async def final_summary(self, messages):
        messages.append({"role": "user", "content": FINAL_SUMMARY_PROMPT})
        final_res = self.brain.call_ai(messages)
        try:
            clean_res = final_res.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r'\{.*\}', clean_res, re.DOTALL)
            data_str = json_match.group(0) if json_match else clean_res
            data = json.loads(data_str)
            return data.get('answer') if isinstance(data, dict) and 'answer' in data else data
        except Exception as e:
            print(f"!!! Lỗi parse tổng hợp: {e}")
            return {
                "summary": "Hệ thống gặp sự cố khi chưng cất tri thức. Vui lòng thử lại.",
                "tech_trends": [],
                "impact_score": 0,
                "sentiment": "Trung tính",
                "sources": []
            }

    async def run_analyst(self, user_prompt: str, context_reports: list):
        context_text = "\n---\n".join([
            f"Tiêu đề: {r.title}\n Tóm tắt: {r.summary}\n Xu hướng: {r.tech_trends}"
            for r in context_reports
        ])

        messages = [
            {"role": "system",
             "content": "Bạn là Chuyên gia Phân tích. Chỉ sử dụng dữ liệu được cung cấp dưới đây để trả lời. Không tự ý tìm thêm thông tin bên ngoài. Nếu không có thông tin, hãy yêu cầu người dùng thực hiện Deep Research."},
            {"role": "system", "content": f"KHO DỮ LIỆU HIỆN CÓ:\n{context_text}"},
            {"role": "user", "content": user_prompt}
        ]

        return self.brain.call_ai(messages)

    async def run(self, topic):
        tool_text = "\n".join([f"- {name}: {info['description']}" for name, info in TOOL_REGISTRY.items()])
        messages = [
            {"role": "system", "content": RESEARCH_SYSTEM_PROMPT.format(tool_descriptions=tool_text)},
            {"role": "user",
             "content": f"Thực hiện nghiên cứu chiến lược chuyên sâu về: {topic}. Yêu cầu tập trung vào số liệu thực tế tại Việt Nam và Toàn cầu."}
        ]
        for i in range(self.max_iterations):
            if i >= self.max_iterations - 2:
                messages.append({"role": "system", "content": FORCE_FINISH_PROMPT})
            raw_res = self.brain.call_ai(messages)
            try:
                clean_res = raw_res.replace("```json", "").replace("```", "").strip()
                json_match = re.search(r'\{.*\}', clean_res, re.DOTALL)
                decision = json.loads(json_match.group(0)) if json_match else json.loads(clean_res)
            except json.JSONDecodeError:
                messages.append({"role": "system", "content": "Lỗi JSON. Hãy trả về đúng định dạng."})
                continue

            print(f"--- Bước {i + 1}: Maestro đang nghĩ: {decision.get('thought')}")

            if decision.get('status') == 'finished':
                return decision.get('answer')

            tool_name = decision.get('tool')
            if tool_name in TOOL_REGISTRY:
                tool_func = TOOL_REGISTRY[tool_name]['func']
                args = decision.get('args', '')
                obs = await tool_func(args) if inspect.iscoroutinefunction(tool_func) else tool_func(args)

                messages.append({"role": "assistant", "content": json.dumps(decision)})
                messages.append({"role": "system", "content": f"Observation: {obs[:3000]}"})
            else:
                messages.append({"role": "system", "content": "Chọn tool hợp lệ hoặc kết thúc."})

        return await self.final_summary(messages)
