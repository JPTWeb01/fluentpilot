from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class RateLimitSnapshot:
    """The rate-limit state reported by a provider's most recent response.

    Not all providers/endpoints report every field (e.g. Groq's transcription
    endpoint has no token-based limit), so the token fields may be None even
    when the request fields are populated.
    """

    limit_requests: int | None
    remaining_requests: int | None
    reset_requests: str | None
    limit_tokens: int | None
    remaining_tokens: int | None
    reset_tokens: str | None


def parse_rate_limit_headers(headers: Mapping[str, str]) -> RateLimitSnapshot | None:
    """Parse Groq's `x-ratelimit-*` response headers, if present."""

    def _int(key: str) -> int | None:
        value = headers.get(key)
        return int(value) if value is not None else None

    limit_requests = _int("x-ratelimit-limit-requests")
    if limit_requests is None:
        return None

    return RateLimitSnapshot(
        limit_requests=limit_requests,
        remaining_requests=_int("x-ratelimit-remaining-requests"),
        reset_requests=headers.get("x-ratelimit-reset-requests"),
        limit_tokens=_int("x-ratelimit-limit-tokens"),
        remaining_tokens=_int("x-ratelimit-remaining-tokens"),
        reset_tokens=headers.get("x-ratelimit-reset-tokens"),
    )


class DailyRequestCounter:
    """Self-tracked request count for providers that report no rate-limit
    headers at all (e.g. Gemini's generateContent endpoint returns none, even
    on a 429 — confirmed by inspecting a live error response's headers).

    This counts requests this process has made against a known static daily
    limit, resetting at UTC midnight. It's an approximation, not a real quota
    read: it undercounts after a process restart and can drift from the
    provider's actual reset boundary (which Google doesn't publish).
    """

    def __init__(self, limit_requests: int) -> None:
        self._limit = limit_requests
        self._count = 0
        self._day = datetime.now(UTC).date()

    def record(self) -> RateLimitSnapshot:
        today = datetime.now(UTC).date()
        if today != self._day:
            self._day = today
            self._count = 0
        self._count += 1

        return RateLimitSnapshot(
            limit_requests=self._limit,
            remaining_requests=max(self._limit - self._count, 0),
            reset_requests=None,
            limit_tokens=None,
            remaining_tokens=None,
            reset_tokens=None,
        )
