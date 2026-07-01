"""Test nhanh kết nối LLM qua brain.py — chạy độc lập, không cần pipeline."""
import asyncio
import sys
from pathlib import Path

# Thêm backend/ vào sys.path để import được app.core
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.core.brain import BrainService


async def main():
    brain = BrainService()

    print("=" * 60)
    print("BrainService Config")
    print(f"  base_url : {brain.base_url}")
    print(f"  api_key  : {brain.api_key[:12]}...{brain.api_key[-4:]}")
    print(f"  low_model: {brain.low_model}")
    print(f"  high_model: {brain.high_model}")
    print("=" * 60)

    # Test 1: low model, sync
    print("\n[1] Sync call_ai (low) ...")
    try:
        reply = brain.call_ai(
            messages=[{"role": "user", "content": "Hello, reply with OK"}],
            model_tier="low",
        )
        print(f"  ✅ Response: {reply}")
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {e}")

    # Test 2: high model, async
    print("\n[2] Async call_ai_async (high) ...")
    try:
        reply = await brain.call_ai_async(
            messages=[{"role": "user", "content": "Hello, reply with OK"}],
            model_tier="high",
        )
        print(f"  ✅ Response: {reply}")
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {e}")

    # Test 3: async, low, force_json
    print("\n[3] Async call_ai_async (low, force_json) ...")
    try:
        reply = await brain.call_ai_async(
            messages=[{"role": "user", "content": "Return JSON: {\"ok\": true}"}],
            model_tier="low",
            force_json=True,
        )
        print(f"  ✅ Response: {reply}")
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
