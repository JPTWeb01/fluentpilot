from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpeechAudio:
    """Synthesized speech, normalized to a single playable format regardless of
    which provider produced it — callers never branch on provider."""

    audio_bytes: bytes
    mime_type: str = "audio/wav"
