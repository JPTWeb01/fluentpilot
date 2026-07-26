from fluentpilot_ai.rate_limit import DailyRequestCounter, parse_rate_limit_headers
from fluentpilot_ai.router import AIOrchestrator
from fluentpilot_ai.speech.router import SpeechOrchestrator
from tests.conftest import FakeProvider, FakeSpeechProvider


def test_parses_full_headers():
    headers = {
        "x-ratelimit-limit-requests": "1000",
        "x-ratelimit-remaining-requests": "988",
        "x-ratelimit-reset-requests": "17m16.8s",
        "x-ratelimit-limit-tokens": "12000",
        "x-ratelimit-remaining-tokens": "11933",
        "x-ratelimit-reset-tokens": "335ms",
    }

    snapshot = parse_rate_limit_headers(headers)

    assert snapshot is not None
    assert snapshot.limit_requests == 1000
    assert snapshot.remaining_requests == 988
    assert snapshot.reset_requests == "17m16.8s"
    assert snapshot.limit_tokens == 12000
    assert snapshot.remaining_tokens == 11933
    assert snapshot.reset_tokens == "335ms"


def test_parses_requests_only_headers():
    # Groq's transcription endpoint reports no token-based limit.
    headers = {
        "x-ratelimit-limit-requests": "2000",
        "x-ratelimit-remaining-requests": "1998",
        "x-ratelimit-reset-requests": "1m26.4s",
    }

    snapshot = parse_rate_limit_headers(headers)

    assert snapshot is not None
    assert snapshot.limit_requests == 2000
    assert snapshot.limit_tokens is None
    assert snapshot.remaining_tokens is None


def test_returns_none_when_headers_absent():
    assert parse_rate_limit_headers({}) is None


async def test_ai_orchestrator_reports_rate_limits(make_request):
    groq = FakeProvider("groq", reply="from groq")
    gemini = FakeProvider("gemini", reply="from gemini")
    orchestrator = AIOrchestrator({"groq": groq, "gemini": gemini})

    assert orchestrator.get_rate_limits() == {"groq": None, "gemini": None}

    groq.rate_limit = parse_rate_limit_headers(
        {"x-ratelimit-limit-requests": "1000", "x-ratelimit-remaining-requests": "999"}
    )

    limits = orchestrator.get_rate_limits()
    assert limits["groq"].remaining_requests == 999
    assert limits["gemini"] is None


def test_daily_request_counter_decrements_remaining_per_call():
    counter = DailyRequestCounter(limit_requests=10)

    first = counter.record()
    second = counter.record()

    assert first.limit_requests == 10
    assert first.remaining_requests == 9
    assert second.remaining_requests == 8


def test_daily_request_counter_floors_at_zero_past_the_limit():
    counter = DailyRequestCounter(limit_requests=1)

    counter.record()
    second = counter.record()

    assert second.remaining_requests == 0


async def test_speech_orchestrator_reports_rate_limits():
    groq = FakeSpeechProvider("groq")
    orchestrator = SpeechOrchestrator({"groq": groq})

    assert orchestrator.get_rate_limits() == {"groq": {"stt": None, "tts": None}}

    groq.stt_rate_limit = parse_rate_limit_headers({"x-ratelimit-limit-requests": "2000"})

    limits = orchestrator.get_rate_limits()
    assert limits["groq"]["stt"].limit_requests == 2000
    assert limits["groq"]["tts"] is None
