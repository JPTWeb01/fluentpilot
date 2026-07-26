import base64

from fastapi import HTTPException, status
from fluentpilot_ai import (
    AIMessage,
    AIOrchestrator,
    AIRequest,
    RateLimitSnapshot,
    SpeechOrchestrator,
)
from fluentpilot_ai.exceptions import AllProvidersFailedError
from fluentpilot_ai.prompts import load_prompt

from src.modules.voice.schemas import (
    ProviderUsage,
    RateLimitInfo,
    UsageResponse,
    VoiceTurnRequest,
    VoiceTurnResponse,
)

SYSTEM_PROMPTS: dict[str, str] = {
    "conversation": load_prompt("conversation"),
    "interview": load_prompt("interview"),
}
MODE_TASKS: dict[str, str] = {
    "conversation": "conversation",
    "interview": "interview_prep",
}


class VoiceService:
    def __init__(
        self, ai_orchestrator: AIOrchestrator, speech_orchestrator: SpeechOrchestrator
    ) -> None:
        self._ai = ai_orchestrator
        self._speech = speech_orchestrator

    async def handle_turn(self, payload: VoiceTurnRequest) -> VoiceTurnResponse:
        try:
            audio_bytes = base64.b64decode(payload.audio_base64, validate=True)
        except Exception as exc:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "audio_base64 is not valid base64."
            ) from exc

        try:
            transcript = await self._speech.transcribe(audio_bytes, payload.mime_type)

            messages = [AIMessage(role="system", content=SYSTEM_PROMPTS[payload.mode])]
            messages.extend(
                AIMessage(role=turn.role, content=turn.content) for turn in payload.history
            )
            messages.append(AIMessage(role="user", content=transcript))

            reply = await self._ai.complete(
                AIRequest(messages=messages, task=MODE_TASKS[payload.mode])
            )
            reply_audio = await self._speech.synthesize(reply.content)
        except AllProvidersFailedError as exc:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "Voice service is temporarily unavailable."
            ) from exc

        return VoiceTurnResponse(
            transcript=transcript,
            reply_text=reply.content,
            reply_audio_base64=base64.b64encode(reply_audio.audio_bytes).decode("ascii"),
        )

    def get_usage(self) -> UsageResponse:
        chat_limits = self._ai.get_rate_limits()
        speech_limits = self._speech.get_rate_limits()

        providers = set(chat_limits) | set(speech_limits)
        return UsageResponse(
            providers={
                name: ProviderUsage(
                    chat=_to_schema(chat_limits.get(name)),
                    stt=_to_schema(speech_limits.get(name, {}).get("stt")),
                    tts=_to_schema(speech_limits.get(name, {}).get("tts")),
                )
                for name in providers
            }
        )


def _to_schema(snapshot: RateLimitSnapshot | None) -> RateLimitInfo | None:
    if snapshot is None:
        return None
    return RateLimitInfo(
        limit_requests=snapshot.limit_requests,
        remaining_requests=snapshot.remaining_requests,
        reset_requests=snapshot.reset_requests,
        limit_tokens=snapshot.limit_tokens,
        remaining_tokens=snapshot.remaining_tokens,
        reset_tokens=snapshot.reset_tokens,
    )
