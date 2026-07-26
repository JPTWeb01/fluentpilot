from fastapi import APIRouter, Depends, Request
from fluentpilot_ai import AIOrchestrator

from src.core.ai import get_ai_orchestrator
from src.core.rate_limit import limiter
from src.deps import get_current_user
from src.modules.auth.models import User
from src.modules.vocabulary.schemas import VocabularyCheckRequest, VocabularyCheckResponse
from src.modules.vocabulary.service import VocabularyService

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.post("/check", response_model=VocabularyCheckResponse)
@limiter.limit("10/minute")
async def check_vocabulary(
    request: Request,
    payload: VocabularyCheckRequest,
    current_user: User = Depends(get_current_user),
    ai_orchestrator: AIOrchestrator = Depends(get_ai_orchestrator),
) -> VocabularyCheckResponse:
    return await VocabularyService(ai_orchestrator).check(payload)
