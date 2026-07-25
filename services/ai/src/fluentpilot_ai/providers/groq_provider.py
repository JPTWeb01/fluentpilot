import groq

from fluentpilot_ai.exceptions import ProviderAPIError, ProviderRateLimitError, ProviderTimeoutError
from fluentpilot_ai.provider_interface import AIProvider
from fluentpilot_ai.types import AIRequest, AIResponse, TokenUsage

DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqProvider(AIProvider):
    """Primary provider — low-latency, used for real-time conversation and
    other quick/simple tasks."""

    name = "groq"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._client = groq.AsyncGroq(api_key=api_key)
        self._model = model

    async def complete(self, request: AIRequest) -> AIResponse:
        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": m.role, "content": m.content} for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except groq.RateLimitError as exc:
            raise ProviderRateLimitError(str(exc)) from exc
        except groq.APITimeoutError as exc:
            raise ProviderTimeoutError(str(exc)) from exc
        except groq.APIError as exc:
            raise ProviderAPIError(str(exc)) from exc

        choice = completion.choices[0]
        usage = completion.usage
        return AIResponse(
            content=choice.message.content or "",
            usage=TokenUsage(
                provider=self.name,
                model=completion.model,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
            ),
            latency_ms=0.0,  # filled in by the orchestrator
        )
