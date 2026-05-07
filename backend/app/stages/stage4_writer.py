from app.core.brain import BrainService
from app.core.prompt import STAGE4_WRITER_PROMPT

class WriterStage:
    def __init__(self):
        self.brain = BrainService()

    def run(self, analysis_data: dict) -> str:
        messages = [
            {"role": "system", "content": STAGE4_WRITER_PROMPT},
            {"role": "user", "content": analysis_data["analysis"]}
        ]
        # Dùng model rẻ để viết lại văn phong là đủ
        return self.brain.call_ai(messages, model_tier="low")