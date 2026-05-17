import litellm
from litellm import completion

from app.core.config import settings

litellm.set_verbose = True


class BrainService:

    def __init__(self):
        self.base_url = settings.OPENROUTER_URL
        self.api_key = settings.OPENROUTER_KEY
        self.high_model = f"openrouter/{settings.HIGH_MODEL}"
        self.low_model = f"openrouter/{settings.LOW_MODEL}"

    def call_ai(self, messages: list, model_tier: str = "low", force_json: bool = False):
        model = self.high_model if model_tier == "high" else self.low_model
        kwargs = {
            "model": model,
            "messages": messages,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": 0.2,
            "max_tokens": 4000,
        }
        if force_json:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            # Call Model By OpenRouter
            response = completion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Lỗi LiteLLM ({model}): {e}")
            raise e

    async def call_ai_async(self, messages: list, model_tier: str = "low", force_json: bool = False):
        model = self.high_model if model_tier == "high" else self.low_model
        kwargs = {
            "model": model,
            "messages": messages,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": 0.2,
            "max_tokens": 4000,
        }
        if force_json:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            from litellm import acompletion
            response = await acompletion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Lỗi LiteLLM Async ({model}): {e}")
            raise e
