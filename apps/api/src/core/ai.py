from functools import lru_cache

from fluentpilot_ai import AIOrchestrator, AIProvider
from fluentpilot_ai.providers.gemini_provider import GeminiProvider
from fluentpilot_ai.providers.groq_provider import GroqProvider
from fluentpilot_ai.providers.ollama_provider import OllamaProvider

from src.core.config import get_settings


def _build_providers() -> dict[str, AIProvider]:
    settings = get_settings()
    providers: dict[str, AIProvider] = {}

    if settings.groq_api_key:
        providers["groq"] = GroqProvider(api_key=settings.groq_api_key, model=settings.groq_model)

    if settings.gemini_api_key:
        providers["gemini"] = GeminiProvider(
            api_key=settings.gemini_api_key, model=settings.gemini_model
        )

    # Ollama has no key — it's a local daemon. Always registered; if nothing is
    # listening at ollama_base_url, requests just fail and the orchestrator
    # reports it via AllProvidersFailedError like any other provider failure.
    providers["ollama"] = OllamaProvider(
        base_url=settings.ollama_base_url, model=settings.ollama_model
    )

    return providers


@lru_cache
def get_ai_orchestrator() -> AIOrchestrator:
    return AIOrchestrator(_build_providers())
