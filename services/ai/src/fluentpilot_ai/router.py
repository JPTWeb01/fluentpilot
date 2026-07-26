import logging
import time
from dataclasses import replace

from fluentpilot_ai.exceptions import AllProvidersFailedError, ProviderError
from fluentpilot_ai.provider_interface import AIProvider
from fluentpilot_ai.rate_limit import RateLimitSnapshot
from fluentpilot_ai.types import AIRequest, AIResponse
from fluentpilot_ai.usage import LoggingUsageRecorder, UsageRecorder

logger = logging.getLogger("fluentpilot_ai.router")

# Simple/quick tasks favor Groq's low latency; complex tasks favor Gemini's reasoning.
# Ollama is always the last-resort fallback (cost, privacy, outage recovery).
SIMPLE_TASK_CHAIN = ["groq", "gemini", "ollama"]
COMPLEX_TASK_CHAIN = ["gemini", "groq", "ollama"]

TASK_CHAINS: dict[str, list[str]] = {
    "conversation": SIMPLE_TASK_CHAIN,
    "grammar": SIMPLE_TASK_CHAIN,
    "vocabulary": SIMPLE_TASK_CHAIN,
    "pronunciation": SIMPLE_TASK_CHAIN,
    "accent": SIMPLE_TASK_CHAIN,
    "interview_prep": COMPLEX_TASK_CHAIN,
    "lesson_generation": COMPLEX_TASK_CHAIN,
    "progress_analysis": COMPLEX_TASK_CHAIN,
}

DEFAULT_CHAIN = SIMPLE_TASK_CHAIN


class AIOrchestrator:
    """Routes a request to the first healthy provider in the task's fallback chain.

    Callers never see which provider answered — that's the point.
    """

    def __init__(
        self,
        providers: dict[str, AIProvider],
        *,
        task_chains: dict[str, list[str]] | None = None,
        usage_recorder: UsageRecorder | None = None,
    ) -> None:
        self._providers = providers
        self._task_chains = task_chains or TASK_CHAINS
        self._usage_recorder = usage_recorder or LoggingUsageRecorder()

    async def complete(self, request: AIRequest) -> AIResponse:
        chain = self._task_chains.get(request.task, DEFAULT_CHAIN)
        errors: dict[str, Exception] = {}

        for provider_name in chain:
            provider = self._providers.get(provider_name)
            if provider is None:
                continue  # not configured in this environment — skip, don't fail

            started = time.perf_counter()
            try:
                response = await provider.complete(request)
            except ProviderError as exc:
                errors[provider_name] = exc
                logger.warning(
                    "ai_provider_failed task=%s provider=%s error=%s",
                    request.task,
                    provider_name,
                    exc,
                )
                continue

            latency_ms = (time.perf_counter() - started) * 1000
            response = replace(response, latency_ms=latency_ms)
            self._usage_recorder.record(
                task=request.task, usage=response.usage, latency_ms=latency_ms
            )
            return response

        raise AllProvidersFailedError(request.task, errors)

    def get_rate_limits(self) -> dict[str, RateLimitSnapshot | None]:
        """Each configured provider's rate-limit state as of its most recent call.

        None for a provider that hasn't been called yet, or that doesn't report
        rate-limit headers at all.
        """
        return {name: provider.rate_limit for name, provider in self._providers.items()}
