import json
from app.core.brain import BrainService
from app.core.prompt import STAGE2_FILTER_PROMPT


class FilterStage:
    def __init__(self):
        self.brain = BrainService()

    def run(self, raw_data_list: list) -> list:
        if not raw_data_list: return []

        messages = [
            {"role": "system", "content": STAGE2_FILTER_PROMPT},
            {"role": "user", "content": json.dumps(raw_data_list, ensure_ascii=False)}
        ]

        # Dùng model giá rẻ (Low Model)
        response = self.brain.call_ai(messages, model_tier="low", force_json=True)
        try:
            parsed = json.loads(response)
            return parsed.get("signals", [])
        except:
            return []