import httpx

from fluentpilot_ai.exceptions import ProviderAPIError, ProviderTimeoutError
from fluentpilot_ai.provider_interface import AIProvider
from fluentpilot_ai.types import AIRequest, AIResponse, TokenUsage

DEFAULT_MODEL = "llama3.1"
DEFAULT_BASE_URL = "http://localhost:11434"


class OllamaProvider(AIProvider):
    """Last-resort local fallback — used when both cloud providers are down,
    or for privacy/cost-sensitive tasks. No API key: it's a local daemon."""

    name = "ollama"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout_seconds: float = 60.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    async def complete(self, request: AIRequest) -> AIResponse:
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "stream": False,
            "options": {"temperature": request.temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise ProviderAPIError(str(exc)) from exc

        data = response.json()
        content = data.get("message", {}).get("content", "")
        # Ollama's /api/chat reports token counts as eval_count/prompt_eval_count, not usage.*.
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        return AIResponse(
            content=content,
            usage=TokenUsage(
                provider=self.name,
                model=self._model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            latency_ms=0.0,
        )
