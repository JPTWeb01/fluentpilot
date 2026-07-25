import groq

from fluentpilot_ai.exceptions import ProviderAPIError, ProviderRateLimitError, ProviderTimeoutError
from fluentpilot_ai.rate_limit import parse_rate_limit_headers
from fluentpilot_ai.speech.provider_interface import SpeechProvider
from fluentpilot_ai.speech.types import SpeechAudio

DEFAULT_STT_MODEL = "whisper-large-v3"
# playai-tts was decommissioned by Groq (shutdown 2025-12-31); orpheus is its
# official replacement. See https://console.groq.com/docs/deprecations.
DEFAULT_TTS_MODEL = "canopylabs/orpheus-v1-english"
DEFAULT_VOICE = "troy"

# Groq's transcription endpoint keys off the filename extension in the multipart
# upload; the mime type on the tuple is what actually tells it the real format.
_EXTENSION_BY_MIME = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/mp4": "mp4",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
}


class GroqSpeechProvider(SpeechProvider):
    """Primary speech provider — low-latency Whisper STT and Orpheus TTS."""

    name = "groq"

    def __init__(
        self,
        api_key: str,
        *,
        stt_model: str = DEFAULT_STT_MODEL,
        tts_model: str = DEFAULT_TTS_MODEL,
        voice: str = DEFAULT_VOICE,
    ) -> None:
        self._client = groq.AsyncGroq(api_key=api_key)
        self._stt_model = stt_model
        self._tts_model = tts_model
        self._voice = voice

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        ext = _EXTENSION_BY_MIME.get(mime_type, "webm")
        try:
            raw = await self._client.audio.transcriptions.with_raw_response.create(
                model=self._stt_model,
                file=(f"audio.{ext}", audio_bytes, mime_type),
            )
        except groq.RateLimitError as exc:
            raise ProviderRateLimitError(str(exc)) from exc
        except groq.APITimeoutError as exc:
            raise ProviderTimeoutError(str(exc)) from exc
        except groq.APIError as exc:
            raise ProviderAPIError(str(exc)) from exc

        self.stt_rate_limit = parse_rate_limit_headers(raw.headers)
        return raw.parse().text

    async def synthesize(self, text: str) -> SpeechAudio:
        try:
            response = await self._client.audio.speech.create(
                model=self._tts_model,
                voice=self._voice,
                input=text,
                response_format="wav",
            )
            audio_bytes = await response.read()
        except groq.RateLimitError as exc:
            raise ProviderRateLimitError(str(exc)) from exc
        except groq.APITimeoutError as exc:
            raise ProviderTimeoutError(str(exc)) from exc
        except groq.APIError as exc:
            raise ProviderAPIError(str(exc)) from exc

        self.tts_rate_limit = parse_rate_limit_headers(response.headers)
        return SpeechAudio(audio_bytes=audio_bytes, mime_type="audio/wav")
