import asyncio
import wave
from io import BytesIO
from pathlib import Path

from piper import PiperVoice

from fluentpilot_ai.exceptions import ProviderAPIError
from fluentpilot_ai.speech.provider_interface import TextToSpeechProvider
from fluentpilot_ai.speech.types import SpeechAudio

DEFAULT_VOICE = "en_US-lessac-medium"
# services/ai/models/piper — voice files are downloaded locally, not committed
# (see README for the download command), so this must exist on disk to work.
DEFAULT_MODELS_DIR = Path(__file__).resolve().parents[4] / "models" / "piper"


class PiperSpeechProvider(TextToSpeechProvider):
    """Last-resort local TTS fallback — synthesizes fully offline via an ONNX
    voice model, so it has no API quota and never depends on Groq/Gemini being
    reachable. Piper has no STT capability, so it only implements TTS and is
    never part of the STT chain.
    """

    name = "piper"

    def __init__(
        self, voice: str = DEFAULT_VOICE, models_dir: Path | str = DEFAULT_MODELS_DIR
    ) -> None:
        self._voice_name = voice
        self._model_path = Path(models_dir) / f"{voice}.onnx"
        self._loaded_voice: PiperVoice | None = None

    def _load(self) -> PiperVoice:
        if self._loaded_voice is None:
            if not self._model_path.exists():
                raise ProviderAPIError(
                    f"Piper voice model not found at {self._model_path}. Download it with: "
                    f"python -m piper.download_voices {self._voice_name} "
                    f"--download-dir {self._model_path.parent}"
                )
            self._loaded_voice = PiperVoice.load(self._model_path)
        return self._loaded_voice

    async def synthesize(self, text: str) -> SpeechAudio:
        return await asyncio.to_thread(self._synthesize_sync, text)

    def _synthesize_sync(self, text: str) -> SpeechAudio:
        voice = self._load()
        try:
            chunks = list(voice.synthesize(text))
        except ProviderAPIError:
            raise
        except Exception as exc:
            raise ProviderAPIError(str(exc)) from exc

        if not chunks:
            raise ProviderAPIError("Piper produced no audio for this text.")

        buffer = BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(chunks[0].sample_channels)
            wav_file.setsampwidth(chunks[0].sample_width)
            wav_file.setframerate(chunks[0].sample_rate)
            for chunk in chunks:
                wav_file.writeframes(chunk.audio_int16_bytes)

        return SpeechAudio(audio_bytes=buffer.getvalue(), mime_type="audio/wav")
