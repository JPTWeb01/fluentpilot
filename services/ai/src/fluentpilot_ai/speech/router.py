import logging

from fluentpilot_ai.exceptions import AllProvidersFailedError, ProviderError
from fluentpilot_ai.speech.provider_interface import SpeechProvider
from fluentpilot_ai.speech.types import SpeechAudio

logger = logging.getLogger("fluentpilot_ai.speech.router")

STT_CHAIN = ["groq", "gemini"]
TTS_CHAIN = ["groq", "gemini"]


class SpeechOrchestrator:
    """Routes transcription/synthesis to the first healthy provider in its chain.

    Parallel to `AIOrchestrator`, kept separate since speech requests/responses
    (raw audio bytes) share no shape with text `AIRequest`/`AIResponse`.
    """

    def __init__(
        self,
        providers: dict[str, SpeechProvider],
        *,
        stt_chain: list[str] | None = None,
        tts_chain: list[str] | None = None,
    ) -> None:
        self._providers = providers
        self._stt_chain = stt_chain or STT_CHAIN
        self._tts_chain = tts_chain or TTS_CHAIN

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        errors: dict[str, Exception] = {}

        for provider_name in self._stt_chain:
            provider = self._providers.get(provider_name)
            if provider is None:
                continue  # not configured in this environment — skip, don't fail

            try:
                return await provider.transcribe(audio_bytes, mime_type)
            except ProviderError as exc:
                errors[provider_name] = exc
                logger.warning(
                    "speech_provider_failed op=transcribe provider=%s error=%s",
                    provider_name,
                    exc,
                )
                continue

        raise AllProvidersFailedError("transcribe", errors)

    async def synthesize(self, text: str) -> SpeechAudio:
        errors: dict[str, Exception] = {}

        for provider_name in self._tts_chain:
            provider = self._providers.get(provider_name)
            if provider is None:
                continue  # not configured in this environment — skip, don't fail

            try:
                return await provider.synthesize(text)
            except ProviderError as exc:
                errors[provider_name] = exc
                logger.warning(
                    "speech_provider_failed op=synthesize provider=%s error=%s",
                    provider_name,
                    exc,
                )
                continue

        raise AllProvidersFailedError("synthesize", errors)
