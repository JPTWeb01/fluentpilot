import json
import re

from fastapi import HTTPException, status
from fluentpilot_ai import AIMessage, AIOrchestrator, AIRequest
from fluentpilot_ai.exceptions import AllProvidersFailedError
from fluentpilot_ai.prompts import load_prompt
from pydantic import ValidationError

from src.modules.accent.schemas import AccentCheckRequest, AccentCheckResponse, AccentTip

SYSTEM_PROMPT = load_prompt("accent")

# Models sometimes wrap JSON in a markdown fence despite instructions not to.
_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


class AccentService:
    def __init__(self, ai_orchestrator: AIOrchestrator) -> None:
        self._ai = ai_orchestrator

    async def check(self, payload: AccentCheckRequest) -> AccentCheckResponse:
        messages = [
            AIMessage(role="system", content=SYSTEM_PROMPT),
            AIMessage(role="user", content=payload.text),
        ]
        try:
            reply = await self._ai.complete(AIRequest(messages=messages, task="accent"))
        except AllProvidersFailedError as exc:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "Accent check is temporarily unavailable.",
            ) from exc

        return AccentCheckResponse(tips=_parse_tips(reply.content))


def _parse_tips(content: str) -> list[AccentTip]:
    cleaned = _JSON_FENCE_RE.sub("", content).strip()
    try:
        items = json.loads(cleaned)
        return [AccentTip(**item) for item in items]
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
        return [AccentTip(phrase="", tip=content.strip())]
