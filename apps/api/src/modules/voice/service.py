import base64

from fastapi import HTTPException, status
from fluentpilot_ai import AIMessage, AIOrchestrator, AIRequest, SpeechOrchestrator
from fluentpilot_ai.exceptions import AllProvidersFailedError
from fluentpilot_ai.prompts import load_prompt

from src.modules.voice.schemas import VoiceTurnRequest, VoiceTurnResponse

SYSTEM_PROMPT = load_prompt("conversation")


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

            messages = [AIMessage(role="system", content=SYSTEM_PROMPT)]
            messages.extend(
                AIMessage(role=turn.role, content=turn.content) for turn in payload.history
            )
            messages.append(AIMessage(role="user", content=transcript))

            reply = await self._ai.complete(AIRequest(messages=messages, task="conversation"))
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
