import os

import litellm
from dotenv import load_dotenv
from litellm import completion

load_dotenv()
litellm.set_verbose = True


class BrainService:
    def __init__(self):
        self.base_url = os.getenv("OPENROUTER_URL")
        self.api_key = os.getenv("OPENROUTER_KEY")
        self.model = f"openrouter/{os.getenv("OPENROUTER_MODEL")}"

    def call_ai(self, messages: list):
        try:
            # Call Gemini Flash By OpenRouter
            response = completion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                base_url=self.base_url,
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"!!! Lỗi LiteLLM: {str(e)}")
            raise e
