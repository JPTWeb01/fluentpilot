"""Manual smoke test — makes a real network call to whichever providers have
an API key set in the environment. Not part of the automated test suite
(no key should ever be required for `pytest` to pass).

Usage (from services/ai/):
    GROQ_API_KEY=... GEMINI_API_KEY=... python scripts/smoke_test.py
"""

import asyncio
import os
import sys

from fluentpilot_ai import AIMessage, AIOrchestrator, AIRequest
from fluentpilot_ai.providers.gemini_provider import GeminiProvider
from fluentpilot_ai.providers.groq_provider import GroqProvider
from fluentpilot_ai.providers.ollama_provider import OllamaProvider


async def main() -> None:
    providers = {}

    if groq_key := os.environ.get("GROQ_API_KEY"):
        providers["groq"] = GroqProvider(api_key=groq_key)
    if gemini_key := os.environ.get("GEMINI_API_KEY"):
        providers["gemini"] = GeminiProvider(api_key=gemini_key)
    if os.environ.get("SKIP_OLLAMA") != "1":
        providers["ollama"] = OllamaProvider()

    if not providers:
        print("No providers configured — set GROQ_API_KEY and/or GEMINI_API_KEY.")
        sys.exit(1)

    print(f"Testing providers: {list(providers)}\n")
    orchestrator = AIOrchestrator(providers)

    request = AIRequest(
        messages=[
            AIMessage(role="system", content="You are a helpful assistant. Reply in one sentence."),
            AIMessage(role="user", content="Say hello and name the model you are."),
        ],
        task="conversation",
    )

    try:
        response = await orchestrator.complete(request)
    except Exception as exc:
        print(f"FAILED: {exc}")
        sys.exit(1)

    print(f"Provider: {response.usage.provider}")
    print(f"Model:    {response.usage.model}")
    print(f"Tokens:   {response.usage.total_tokens}")
    print(f"Latency:  {response.latency_ms:.0f}ms")
    print(f"Reply:    {response.content}")


if __name__ == "__main__":
    asyncio.run(main())
