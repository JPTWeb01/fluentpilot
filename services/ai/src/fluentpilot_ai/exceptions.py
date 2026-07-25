class ProviderError(Exception):
    """Base class for expected, fallback-worthy provider failures.

    Provider adapters must raise this (or a subclass) — never a raw SDK/HTTP
    exception — so the orchestrator can decide whether to fall back. Anything
    else (a real bug in the adapter) propagates normally instead of being
    mistaken for a transient provider failure.
    """


class ProviderTimeoutError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    pass


class ProviderAPIError(ProviderError):
    pass


class AllProvidersFailedError(Exception):
    def __init__(self, task: str, errors: dict[str, Exception]) -> None:
        self.task = task
        self.errors = errors
        summary = (
            ", ".join(f"{name}: {err}" for name, err in errors.items())
            or "no providers configured"
        )
        super().__init__(f"All providers failed for task '{task}': {summary}")
