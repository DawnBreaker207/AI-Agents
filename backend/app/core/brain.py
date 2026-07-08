import asyncio
import logging
import time

from litellm import completion, acompletion
from litellm.exceptions import RateLimitError

from app.core.config import settings

logger = logging.getLogger(__name__)

_MAX_RETRIES = 5
_BASE_DELAY = 10  # seconds (exponential: 10s, 20s, 40s, 80s, 160s)


class BrainService:

    def __init__(self):
        self.base_url = settings.LLM_API_BASE
        self.api_key = settings.LLM_API_KEY
        # Dùng prefix "openai/" + model id gốc (vd "opencode/deepseek-v4-flash-free")
        # để litellm dùng provider OpenAI-compatible, gọi tới api_base tuỳ chỉnh
        self.high_model = f"openai/{settings.HIGH_MODEL}"
        self.low_model = f"openai/{settings.LOW_MODEL}"

    def _build_kwargs(self, model: str, messages: list, force_json: bool) -> dict:
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
        return kwargs

    def call_ai(self, messages: list, model_tier: str = "low", force_json: bool = False):
        model = self.high_model if model_tier == "high" else self.low_model
        kwargs = self._build_kwargs(model, messages, force_json)

        for attempt in range(_MAX_RETRIES):
            try:
                response = completion(**kwargs)
                return response.choices[0].message.content
            except RateLimitError:
                if attempt < _MAX_RETRIES - 1:
                    delay = _BASE_DELAY * (2 ** attempt)
                    print(f"[Brain] Rate limited ({model}), retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"[Brain] Rate limit exceeded ({model}) after {_MAX_RETRIES} retries")
                    raise
            except Exception as e:
                print(f"[Brain] LLM error ({model}): {e}")
                raise

    async def call_ai_async(self, messages: list, model_tier: str = "low", force_json: bool = False):
        model = self.high_model if model_tier == "high" else self.low_model
        kwargs = self._build_kwargs(model, messages, force_json)

        for attempt in range(_MAX_RETRIES):
            try:
                response = await acompletion(**kwargs)
                return response.choices[0].message.content
            except RateLimitError:
                if attempt < _MAX_RETRIES - 1:
                    delay = _BASE_DELAY * (2 ** attempt)
                    print(f"[Brain] Rate limited ({model}), retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"[Brain] Rate limit exceeded ({model}) after {_MAX_RETRIES} retries")
                    raise
            except Exception as e:
                print(f"[Brain] LLM error async ({model}): {e}")
                raise
