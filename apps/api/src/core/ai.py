from functools import lru_cache

from fluentpilot_ai import (
    AIOrchestrator,
    AIProvider,
    SpeechOrchestrator,
    SpeechToTextProvider,
    TextToSpeechProvider,
)
from fluentpilot_ai.providers.gemini_provider import GeminiProvider
from fluentpilot_ai.providers.groq_provider import GroqProvider
from fluentpilot_ai.providers.ollama_provider import OllamaProvider
from fluentpilot_ai.speech.providers.gemini_speech_provider import GeminiSpeechProvider
from fluentpilot_ai.speech.providers.groq_speech_provider import GroqSpeechProvider
from fluentpilot_ai.speech.providers.piper_speech_provider import PiperSpeechProvider

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


def _build_speech_providers() -> dict[str, SpeechToTextProvider | TextToSpeechProvider]:
    settings = get_settings()
    providers: dict[str, SpeechToTextProvider | TextToSpeechProvider] = {}

    if settings.groq_api_key:
        providers["groq"] = GroqSpeechProvider(
            api_key=settings.groq_api_key,
            stt_model=settings.groq_stt_model,
            tts_model=settings.groq_tts_model,
        )

    if settings.gemini_api_key:
        providers["gemini"] = GeminiSpeechProvider(
            api_key=settings.gemini_api_key, tts_model=settings.gemini_tts_model
        )

    # No API key — fully local/offline TTS-only fallback, always registered.
    # If the voice model hasn't been downloaded, synthesis just fails like any
    # other provider failure and the orchestrator falls through past it.
    providers["piper"] = PiperSpeechProvider(voice=settings.piper_voice)

    # No Ollama entry — it has no STT/TTS capability.
    return providers


@lru_cache
def get_speech_orchestrator() -> SpeechOrchestrator:
    return SpeechOrchestrator(_build_speech_providers())
