from collections.abc import Mapping
from dataclasses import dataclass


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
