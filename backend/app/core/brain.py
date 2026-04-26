import requests
import litellm
from litellm import completion
from config import settings

litellm.set_verbose = True


class BrainService:
    def __init__(self):
        self.base_url = settings.OPENROUTER_URL
        self.api_key = settings.OPENROUTER_KEY
        self.model = f"openrouter/{settings.OPENROUTER_MODEL}"

    def call_ai(self, messages: list):
        try:
            # Call Gemini Flash By OpenRouter
            response = completion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                base_url=self.base_url,
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0.5,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"!!! Lỗi LiteLLM: {str(e)}")
            raise e

    def get_credit_balance(self):
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
            if response.status_code == 200:
                data = response.json()
                limit = data['data']['limit']
                usage = data['data']['usage']
                remaining = limit - usage
                return round(remaining, 4)
            return 0
        except Exception as e:
            print(f"Lỗi check balance: {e}")
            return 0
