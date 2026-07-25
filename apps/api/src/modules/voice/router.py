from fastapi import APIRouter, Depends, Request
from fluentpilot_ai import AIOrchestrator, SpeechOrchestrator

from src.core.ai import get_ai_orchestrator, get_speech_orchestrator
from src.core.rate_limit import limiter
from src.deps import get_current_user
from src.modules.auth.models import User
from src.modules.voice.schemas import VoiceTurnRequest, VoiceTurnResponse
from src.modules.voice.service import VoiceService

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/turns", response_model=VoiceTurnResponse)
@limiter.limit("6/minute")
async def create_turn(
    request: Request,
    payload: VoiceTurnRequest,
    current_user: User = Depends(get_current_user),
    ai_orchestrator: AIOrchestrator = Depends(get_ai_orchestrator),
    speech_orchestrator: SpeechOrchestrator = Depends(get_speech_orchestrator),
) -> VoiceTurnResponse:
    return await VoiceService(ai_orchestrator, speech_orchestrator).handle_turn(payload)
