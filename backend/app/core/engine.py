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
            json_match = re.search(r'\{.*\}', final_res, re.DOTALL)
            clean_res = json_match.group(0) if json_match else final_res
            data = json.loads(clean_res)
            return data.get('answer') if 'answer' in data else data
        except:
            return {"summary": "Không thể tổng hợp báo cáo.", "tech_trends": [], "impact_score": 0}

    async def run(self, topic):
        tool_text = "\n".join([f"- {name}: {info['description']}" for name, info in TOOL_REGISTRY.items()])
        messages = [
            {"role": "system", "content": RESEARCH_SYSTEM_PROMPT.format(tool_descriptions=tool_text)},
            {"role": "user", "content": f"Nghiên cứu chuyên sâu về: {topic}"}
        ]
        for i in range(self.max_iterations):
            if i >= self.max_iterations - 2:
                messages.append({"role": "system", "content": FORCE_FINISH_PROMPT})
            raw_res = self.brain.call_ai(messages)
            try:
                json_match = re.search(r'\{.*\}', raw_res, re.DOTALL)
                decision = json.loads(json_match.group(0)) if json_match else json.loads(raw_res)
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
                messages.append({"role": "system", "content": f"Observation: {obs[:2000]}"})
            else:
                messages.append({"role": "system", "content": "Chọn tool hợp lệ hoặc kết thúc."})

        return await self._final_summary(messages)
