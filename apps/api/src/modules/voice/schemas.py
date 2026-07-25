from typing import Literal

from pydantic import BaseModel, Field

# Base64 of raw audio; ~15MB of decoded audio is a generous cap for a single
# push-to-talk utterance, this just guards against wildly oversized payloads.
MAX_AUDIO_BASE64_LENGTH = 20_000_000


class VoiceMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class VoiceTurnRequest(BaseModel):
    audio_base64: str = Field(max_length=MAX_AUDIO_BASE64_LENGTH)
    mime_type: str
    history: list[VoiceMessage] = Field(default_factory=list)


class VoiceTurnResponse(BaseModel):
    transcript: str
    reply_text: str
    reply_audio_base64: str
