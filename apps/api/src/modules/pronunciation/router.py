from fastapi import APIRouter, Depends, Request
from fluentpilot_ai import AIOrchestrator

from src.core.ai import get_ai_orchestrator
from src.core.rate_limit import limiter
from src.deps import get_current_user
from src.modules.auth.models import User
from src.modules.pronunciation.schemas import (
    PronunciationCheckRequest,
    PronunciationCheckResponse,
)
from src.modules.pronunciation.service import PronunciationService

router = APIRouter(prefix="/pronunciation", tags=["pronunciation"])


@router.post("/check", response_model=PronunciationCheckResponse)
@limiter.limit("10/minute")
async def check_pronunciation(
    request: Request,
    payload: PronunciationCheckRequest,
    current_user: User = Depends(get_current_user),
    ai_orchestrator: AIOrchestrator = Depends(get_ai_orchestrator),
) -> PronunciationCheckResponse:
    return await PronunciationService(ai_orchestrator).check(payload)
