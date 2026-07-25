from abc import ABC, abstractmethod

from fluentpilot_ai.rate_limit import RateLimitSnapshot
from fluentpilot_ai.speech.types import SpeechAudio


class SpeechToTextProvider(ABC):
    name: str

    # See AIProvider.rate_limit — same idea, tracked separately from TTS since
    # STT/TTS are different endpoints with independent limits.
    stt_rate_limit: RateLimitSnapshot | None = None

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        """Transcribe spoken audio to text.

        Implementations must raise a `ProviderError` subclass (not a raw SDK/HTTP
        exception) on failure so the orchestrator can decide whether to fall back.
        """


class TextToSpeechProvider(ABC):
    name: str

    tts_rate_limit: RateLimitSnapshot | None = None

    @abstractmethod
    async def synthesize(self, text: str) -> SpeechAudio:
        """Synthesize text to speech.

        Implementations must raise a `ProviderError` subclass (not a raw SDK/HTTP
        exception) on failure so the orchestrator can decide whether to fall back.
        """


class SpeechProvider(SpeechToTextProvider, TextToSpeechProvider):
    """A provider implementing both directions of the speech round-trip.

    Used purely as a type annotation target — vendor adapters that own a single
    SDK client for both STT and TTS (e.g. Groq, Gemini) inherit from this instead
    of each interface separately.
    """
