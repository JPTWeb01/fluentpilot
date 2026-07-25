import base64

from fluentpilot_ai import AIRequest, AIResponse, RateLimitSnapshot, SpeechAudio, TokenUsage
from fluentpilot_ai.exceptions import AllProvidersFailedError

from src.core.ai import get_ai_orchestrator, get_speech_orchestrator
from src.main import app


class FakeAIOrchestrator:
    def __init__(self, *, reply: str = "Nice to hear from you!", fails: bool = False) -> None:
        self._reply = reply
        self._fails = fails
        self.requests: list[AIRequest] = []

    async def complete(self, request: AIRequest) -> AIResponse:
        self.requests.append(request)
        if self._fails:
            raise AllProvidersFailedError("conversation", {"groq": Exception("down")})
        return AIResponse(
            content=self._reply,
            usage=TokenUsage(
                provider="fake",
                model="fake-model",
                prompt_tokens=1,
                completion_tokens=1,
                total_tokens=2,
            ),
            latency_ms=0.0,
        )

    def get_rate_limits(self) -> dict[str, RateLimitSnapshot | None]:
        return {"groq": RateLimitSnapshot(1000, 999, "1m", None, None, None)}


class FakeSpeechOrchestrator:
    def __init__(self, *, transcript: str = "hello there", fails: bool = False) -> None:
        self._transcript = transcript
        self._fails = fails
        self.transcribe_calls: list[tuple[bytes, str]] = []
        self.synthesize_calls: list[str] = []

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        self.transcribe_calls.append((audio_bytes, mime_type))
        if self._fails:
            raise AllProvidersFailedError("transcribe", {"groq": Exception("down")})
        return self._transcript

    async def synthesize(self, text: str) -> SpeechAudio:
        self.synthesize_calls.append(text)
        if self._fails:
            raise AllProvidersFailedError("synthesize", {"groq": Exception("down")})
        return SpeechAudio(audio_bytes=b"fake-wav-bytes", mime_type="audio/wav")

    def get_rate_limits(self) -> dict[str, dict[str, RateLimitSnapshot | None]]:
        return {"groq": {"stt": RateLimitSnapshot(2000, 1998, "1m", None, None, None), "tts": None}}


async def _authed_headers(client) -> dict[str, str]:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "speaker@example.com", "password": "correct-horse-battery"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_voice_turn_returns_transcript_reply_and_audio(client):
    headers = await _authed_headers(client)
    fake_ai = FakeAIOrchestrator(reply="Tell me more about your day.")
    fake_speech = FakeSpeechOrchestrator(transcript="I went for a walk today")
    app.dependency_overrides[get_ai_orchestrator] = lambda: fake_ai
    app.dependency_overrides[get_speech_orchestrator] = lambda: fake_speech

    audio_b64 = base64.b64encode(b"raw-audio-bytes").decode("ascii")
    resp = await client.post(
        "/api/v1/voice/turns",
        json={"audio_base64": audio_b64, "mime_type": "audio/webm", "history": []},
        headers=headers,
    )

    del app.dependency_overrides[get_ai_orchestrator]
    del app.dependency_overrides[get_speech_orchestrator]

    assert resp.status_code == 200
    body = resp.json()
    assert body["transcript"] == "I went for a walk today"
    assert body["reply_text"] == "Tell me more about your day."
    assert base64.b64decode(body["reply_audio_base64"]) == b"fake-wav-bytes"

    assert fake_speech.transcribe_calls == [(b"raw-audio-bytes", "audio/webm")]
    assert fake_speech.synthesize_calls == ["Tell me more about your day."]
    assert fake_ai.requests[0].messages[-1].content == "I went for a walk today"


async def test_voice_turn_requires_auth(client):
    audio_b64 = base64.b64encode(b"raw-audio-bytes").decode("ascii")
    resp = await client.post(
        "/api/v1/voice/turns",
        json={"audio_base64": audio_b64, "mime_type": "audio/webm", "history": []},
    )
    assert resp.status_code in (401, 403)


async def test_voice_turn_rejects_invalid_base64(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator()
    app.dependency_overrides[get_speech_orchestrator] = lambda: FakeSpeechOrchestrator()

    resp = await client.post(
        "/api/v1/voice/turns",
        json={"audio_base64": "not-valid-base64!!", "mime_type": "audio/webm", "history": []},
        headers=headers,
    )

    del app.dependency_overrides[get_ai_orchestrator]
    del app.dependency_overrides[get_speech_orchestrator]

    assert resp.status_code == 422


async def test_voice_turn_returns_503_when_all_speech_providers_fail(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator()
    app.dependency_overrides[get_speech_orchestrator] = lambda: FakeSpeechOrchestrator(fails=True)

    audio_b64 = base64.b64encode(b"raw-audio-bytes").decode("ascii")
    resp = await client.post(
        "/api/v1/voice/turns",
        json={"audio_base64": audio_b64, "mime_type": "audio/webm", "history": []},
        headers=headers,
    )

    del app.dependency_overrides[get_ai_orchestrator]
    del app.dependency_overrides[get_speech_orchestrator]

    assert resp.status_code == 503


async def test_get_usage_returns_rate_limit_snapshot(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator()
    app.dependency_overrides[get_speech_orchestrator] = lambda: FakeSpeechOrchestrator()

    resp = await client.get("/api/v1/voice/usage", headers=headers)

    del app.dependency_overrides[get_ai_orchestrator]
    del app.dependency_overrides[get_speech_orchestrator]

    assert resp.status_code == 200
    groq = resp.json()["providers"]["groq"]
    assert groq["chat"] == {
        "limit_requests": 1000,
        "remaining_requests": 999,
        "reset_requests": "1m",
        "limit_tokens": None,
        "remaining_tokens": None,
        "reset_tokens": None,
    }
    assert groq["stt"]["remaining_requests"] == 1998
    assert groq["tts"] is None


async def test_get_usage_requires_auth(client):
    resp = await client.get("/api/v1/voice/usage")
    assert resp.status_code in (401, 403)
