from abc import ABC, abstractmethod

from fluentpilot_ai.rate_limit import RateLimitSnapshot
from fluentpilot_ai.types import AIRequest, AIResponse


class AIProvider(ABC):
    name: str

    # Snapshot of rate-limit headers from this provider's most recent response,
    # if it reports any (see `rate_limit.parse_rate_limit_headers`). None until
    # a request has been made, and always None for providers that don't report it.
    rate_limit: RateLimitSnapshot | None = None

    @abstractmethod
    async def complete(self, request: AIRequest) -> AIResponse:
        """Send the request to the underlying model and return a normalized response.

        Implementations must raise a `ProviderError` subclass (not a raw SDK/HTTP
        exception) on failure so the orchestrator can decide whether to fall back.
        """
