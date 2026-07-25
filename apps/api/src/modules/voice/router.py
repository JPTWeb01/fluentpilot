from fastapi import APIRouter, Depends, Request
from fluentpilot_ai import AIOrchestrator, SpeechOrchestrator

from src.core.ai import get_ai_orchestrator, get_speech_orchestrator
from src.core.rate_limit import limiter
from src.deps import get_current_user
from src.modules.auth.models import User
from src.modules.voice.schemas import UsageResponse, VoiceTurnRequest, VoiceTurnResponse
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


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    ai_orchestrator: AIOrchestrator = Depends(get_ai_orchestrator),
    speech_orchestrator: SpeechOrchestrator = Depends(get_speech_orchestrator),
) -> UsageResponse:
    """Rate-limit state as of each provider's most recent call this server run.

    Reads in-memory state only (no external API calls), so it's safe to poll
    freely. Fields are null until the relevant provider/operation has been
    used at least once.
    """
    return VoiceService(ai_orchestrator, speech_orchestrator).get_usage()
