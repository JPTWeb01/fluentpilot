from fastapi import APIRouter, Depends, Request
from fluentpilot_ai import AIOrchestrator

from src.core.ai import get_ai_orchestrator
from src.core.rate_limit import limiter
from src.deps import get_current_user
from src.modules.accent.schemas import AccentCheckRequest, AccentCheckResponse
from src.modules.accent.service import AccentService
from src.modules.auth.models import User

router = APIRouter(prefix="/accent", tags=["accent"])


@router.post("/check", response_model=AccentCheckResponse)
@limiter.limit("10/minute")
async def check_accent(
    request: Request,
    payload: AccentCheckRequest,
    current_user: User = Depends(get_current_user),
    ai_orchestrator: AIOrchestrator = Depends(get_ai_orchestrator),
) -> AccentCheckResponse:
    return await AccentService(ai_orchestrator).check(payload)
