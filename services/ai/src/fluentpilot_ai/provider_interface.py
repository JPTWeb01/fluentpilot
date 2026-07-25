from abc import ABC, abstractmethod

from fluentpilot_ai.types import AIRequest, AIResponse


class AIProvider(ABC):
    name: str

    @abstractmethod
    async def complete(self, request: AIRequest) -> AIResponse:
        """Send the request to the underlying model and return a normalized response.

        Implementations must raise a `ProviderError` subclass (not a raw SDK/HTTP
        exception) on failure so the orchestrator can decide whether to fall back.
        """
