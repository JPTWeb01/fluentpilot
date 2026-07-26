import io
import re
import wave

from google import genai
from google.genai import errors, types

from fluentpilot_ai.exceptions import ProviderAPIError, ProviderRateLimitError, ProviderTimeoutError
from fluentpilot_ai.rate_limit import DailyRequestCounter
from fluentpilot_ai.speech.provider_interface import SpeechProvider
from fluentpilot_ai.speech.types import SpeechAudio

DEFAULT_STT_MODEL = "gemini-2.0-flash"
DEFAULT_TTS_MODEL = "gemini-2.5-flash-preview-tts"
DEFAULT_VOICE = "Kore"

# Empirically confirmed (not published in Gemini's rate-limit docs, which just
# point at the AI Studio dashboard): the free tier caps gemini-2.5-flash-preview-tts
# at exactly 10 requests/day/project. Gemini's chat/STT models have no similarly
# confirmed number, so only TTS gets a self-tracked counter — see DailyRequestCounter.
_TTS_DAILY_LIMIT = 10

_TRANSCRIBE_INSTRUCTION = (
    "Transcribe this audio verbatim. Reply with only the transcript, no commentary."
)

# Gemini's native audio output is raw PCM (no container) at a rate given in the
# response's mime type, e.g. "audio/L16;codec=pcm;rate=24000" — 16-bit mono unless
# documented otherwise. A browser can't play headerless PCM, so we wrap it in WAV.
_DEFAULT_SAMPLE_RATE = 24000
_SAMPLE_WIDTH_BYTES = 2
_CHANNELS = 1


def _pcm_to_wav(pcm_bytes: bytes, mime_type: str) -> bytes:
    rate_match = re.search(r"rate=(\d+)", mime_type)
    sample_rate = int(rate_match.group(1)) if rate_match else _DEFAULT_SAMPLE_RATE

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(_CHANNELS)
        wav_file.setsampwidth(_SAMPLE_WIDTH_BYTES)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)
    return buffer.getvalue()


class GeminiSpeechProvider(SpeechProvider):
    """Fallback speech provider — multimodal transcription and native TTS."""

    name = "gemini"

    def __init__(
        self,
        api_key: str,
        *,
        stt_model: str = DEFAULT_STT_MODEL,
        tts_model: str = DEFAULT_TTS_MODEL,
        voice: str = DEFAULT_VOICE,
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._stt_model = stt_model
        self._tts_model = tts_model
        self._voice = voice
        self._tts_counter = DailyRequestCounter(_TTS_DAILY_LIMIT)

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    types.Part(text=_TRANSCRIBE_INSTRUCTION),
                ],
            )
        ]
        try:
            response = await self._client.aio.models.generate_content(
                model=self._stt_model, contents=contents
            )
        except errors.ClientError as exc:
            if exc.code == 429:
                raise ProviderRateLimitError(str(exc)) from exc
            raise ProviderAPIError(str(exc)) from exc
        except errors.ServerError as exc:
            if exc.code == 504:
                raise ProviderTimeoutError(str(exc)) from exc
            raise ProviderAPIError(str(exc)) from exc
        except errors.APIError as exc:
            raise ProviderAPIError(str(exc)) from exc

        return (response.text or "").strip()

    async def synthesize(self, text: str) -> SpeechAudio:
        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self._voice)
                )
            ),
        )
        try:
            response = await self._client.aio.models.generate_content(
                model=self._tts_model, contents=text, config=config
            )
        except errors.ClientError as exc:
            if exc.code == 429:
                raise ProviderRateLimitError(str(exc)) from exc
            raise ProviderAPIError(str(exc)) from exc
        except errors.ServerError as exc:
            if exc.code == 504:
                raise ProviderTimeoutError(str(exc)) from exc
            raise ProviderAPIError(str(exc)) from exc
        except errors.APIError as exc:
            raise ProviderAPIError(str(exc)) from exc

        try:
            inline_data = response.candidates[0].content.parts[0].inline_data
        except (IndexError, AttributeError, TypeError) as exc:
            raise ProviderAPIError("Gemini TTS response contained no audio") from exc
        if inline_data is None or inline_data.data is None:
            raise ProviderAPIError("Gemini TTS response contained no audio")

        self.tts_rate_limit = self._tts_counter.record()

        wav_bytes = _pcm_to_wav(inline_data.data, inline_data.mime_type or "")
        return SpeechAudio(audio_bytes=wav_bytes, mime_type="audio/wav")
