from fastapi import APIRouter, Depends, Request
from fluentpilot_ai import AIOrchestrator

from src.core.ai import get_ai_orchestrator
from src.core.rate_limit import limiter
from src.deps import get_current_user
from src.modules.auth.models import User
from src.modules.grammar.schemas import GrammarCheckRequest, GrammarCheckResponse
from src.modules.grammar.service import GrammarService

router = APIRouter(prefix="/grammar", tags=["grammar"])


@router.post("/check", response_model=GrammarCheckResponse)
@limiter.limit("10/minute")
async def check_grammar(
    request: Request,
    payload: GrammarCheckRequest,
    current_user: User = Depends(get_current_user),
    ai_orchestrator: AIOrchestrator = Depends(get_ai_orchestrator),
) -> GrammarCheckResponse:
    return await GrammarService(ai_orchestrator).check(payload)
