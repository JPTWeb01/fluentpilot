from fluentpilot_ai import AIRequest, AIResponse, TokenUsage
from fluentpilot_ai.exceptions import AllProvidersFailedError

from src.core.ai import get_ai_orchestrator
from src.main import app


class FakeAIOrchestrator:
    def __init__(self, *, reply: str = "[]", fails: bool = False) -> None:
        self._reply = reply
        self._fails = fails
        self.requests: list[AIRequest] = []

    async def complete(self, request: AIRequest) -> AIResponse:
        self.requests.append(request)
        if self._fails:
            raise AllProvidersFailedError("accent", {"groq": Exception("down")})
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


async def _authed_headers(client) -> dict[str, str]:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "accent-tester@example.com", "password": "correct-horse-battery"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_accent_check_returns_parsed_tips(client):
    headers = await _authed_headers(client)
    reply = (
        '[{"phrase": "think", '
        '"tip": "Try tapping your tongue behind your top teeth for a crisper th sound."}]'
    )
    fake_ai = FakeAIOrchestrator(reply=reply)
    app.dependency_overrides[get_ai_orchestrator] = lambda: fake_ai

    resp = await client.post(
        "/api/v1/accent/check",
        json={"text": "I tink this is a good idea"},
        headers=headers,
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 200
    body = resp.json()
    assert body["tips"] == [
        {
            "phrase": "think",
            "tip": "Try tapping your tongue behind your top teeth for a crisper th sound.",
        }
    ]
    assert fake_ai.requests[0].task == "accent"


async def test_accent_check_returns_empty_list_when_nothing_stands_out(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator(reply="[]")

    resp = await client.post(
        "/api/v1/accent/check", json={"text": "the cat sat on the mat"}, headers=headers
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 200
    assert resp.json()["tips"] == []


async def test_accent_check_falls_back_softly_on_malformed_json(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator(
        reply="Sorry, I can't help with that."
    )

    resp = await client.post(
        "/api/v1/accent/check",
        json={"text": "I tink this is a good idea"},
        headers=headers,
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 200
    tips = resp.json()["tips"]
    assert len(tips) == 1
    assert tips[0]["phrase"] == ""
    assert tips[0]["tip"] == "Sorry, I can't help with that."


async def test_accent_check_returns_503_when_all_providers_fail(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator(fails=True)

    resp = await client.post(
        "/api/v1/accent/check",
        json={"text": "I tink this is a good idea"},
        headers=headers,
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 503


async def test_accent_check_requires_auth(client):
    resp = await client.post(
        "/api/v1/accent/check", json={"text": "I tink this is a good idea"}
    )
    assert resp.status_code in (401, 403)


async def test_accent_check_rejects_empty_text(client):
    headers = await _authed_headers(client)
    resp = await client.post(
        "/api/v1/accent/check", json={"text": ""}, headers=headers
    )
    assert resp.status_code == 422
