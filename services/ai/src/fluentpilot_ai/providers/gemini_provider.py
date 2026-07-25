from google import genai
from google.genai import errors, types

from fluentpilot_ai.exceptions import ProviderAPIError, ProviderRateLimitError, ProviderTimeoutError
from fluentpilot_ai.provider_interface import AIProvider
from fluentpilot_ai.types import AIRequest, AIResponse, TokenUsage

DEFAULT_MODEL = "gemini-2.0-flash"

# Gemini has no separate "system" role — a system message becomes config.system_instruction,
# and the remaining turns must alternate user/model.
_ROLE_MAP = {"user": "user", "assistant": "model"}


class GeminiProvider(AIProvider):
    """Secondary provider — used for complex reasoning: lesson generation,
    interview prep, progress analysis."""

    name = "gemini"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def complete(self, request: AIRequest) -> AIResponse:
        system_instruction = None
        contents: list[types.Content] = []
        for message in request.messages:
            if message.role == "system":
                system_instruction = message.content
                continue
            contents.append(
                types.Content(
                    role=_ROLE_MAP[message.role],
                    parts=[types.Part(text=message.content)],
                )
            )

        config = types.GenerateContentConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
            system_instruction=system_instruction,
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )
        except errors.ClientError as exc:
            if exc.code == 429:
                raise ProviderRateLimitError(str(exc)) from exc
            raise ProviderAPIError(str(exc)) from exc
        except errors.ServerError as exc:
            if exc.code == 504:
                raise ProviderTimeoutError(str(exc)) from exc
            raise ProviderAPIError(str(exc)) from exc
        except errors.APIError as exc:
            raise ProviderAPIError(str(exc)) from exc

        usage = response.usage_metadata
        return AIResponse(
            content=response.text or "",
            usage=TokenUsage(
                provider=self.name,
                model=self._model,
                prompt_tokens=usage.prompt_token_count if usage else 0,
                completion_tokens=usage.candidates_token_count if usage else 0,
                total_tokens=usage.total_token_count if usage else 0,
            ),
            latency_ms=0.0,
        )
