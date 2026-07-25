import logging
from typing import Protocol

from fluentpilot_ai.types import TokenUsage

logger = logging.getLogger("fluentpilot_ai.usage")


class UsageRecorder(Protocol):
    def record(self, *, task: str, usage: TokenUsage, latency_ms: float) -> None: ...


class LoggingUsageRecorder:
    """Default recorder — logs usage. Phase 6 swaps in a DB-backed recorder for
    cost tracking/dashboards without the orchestrator needing to change."""

    def record(self, *, task: str, usage: TokenUsage, latency_ms: float) -> None:
        logger.info(
            "ai_usage task=%s provider=%s model=%s prompt_tokens=%d completion_tokens=%d "
            "total_tokens=%d latency_ms=%.1f",
            task,
            usage.provider,
            usage.model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
            latency_ms,
        )
