import pytest

from fluentpilot_ai.exceptions import ProviderAPIError
from fluentpilot_ai.provider_interface import AIProvider
from fluentpilot_ai.types import AIRequest, AIResponse, TokenUsage


class FakeProvider(AIProvider):
    """Test double: either returns a canned response or raises ProviderError,
    and records every request it was called with."""

    def __init__(self, name: str, *, fails: bool = False, reply: str = "ok") -> None:
        self.name = name
        self._fails = fails
        self._reply = reply
        self.calls: list[AIRequest] = []

    async def complete(self, request: AIRequest) -> AIResponse:
        self.calls.append(request)
        if self._fails:
            raise ProviderAPIError(f"{self.name} is down")
        return AIResponse(
            content=self._reply,
            usage=TokenUsage(
                provider=self.name,
                model="fake-model",
                prompt_tokens=1,
                completion_tokens=1,
                total_tokens=2,
            ),
            latency_ms=0.0,
        )


@pytest.fixture
def make_request():
    def _make(task: str = "conversation") -> AIRequest:
        from fluentpilot_ai.types import AIMessage

        return AIRequest(messages=[AIMessage(role="user", content="hello")], task=task)

    return _make
