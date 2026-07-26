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
            raise AllProvidersFailedError("grammar", {"groq": Exception("down")})
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
        json={"email": "grammar-tester@example.com", "password": "correct-horse-battery"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_grammar_check_returns_parsed_corrections(client):
    headers = await _authed_headers(client)
    reply = (
        '[{"original": "she don\'t like", "corrected": "she doesn\'t like", '
        '"explanation": "Use \\"doesn\'t\\" with he/she/it."}]'
    )
    fake_ai = FakeAIOrchestrator(reply=reply)
    app.dependency_overrides[get_ai_orchestrator] = lambda: fake_ai

    resp = await client.post(
        "/api/v1/grammar/check", json={"text": "she don't like coffee"}, headers=headers
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 200
    body = resp.json()
    assert body["corrections"] == [
        {
            "original": "she don't like",
            "corrected": "she doesn't like",
            "explanation": "Use \"doesn't\" with he/she/it.",
        }
    ]
    assert fake_ai.requests[0].task == "grammar"


async def test_grammar_check_returns_empty_list_when_no_mistakes(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator(reply="[]")

    resp = await client.post(
        "/api/v1/grammar/check", json={"text": "She doesn't like coffee."}, headers=headers
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 200
    assert resp.json()["corrections"] == []


async def test_grammar_check_falls_back_softly_on_malformed_json(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator(
        reply="Sorry, I can't help with that."
    )

    resp = await client.post(
        "/api/v1/grammar/check", json={"text": "she don't like coffee"}, headers=headers
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 200
    corrections = resp.json()["corrections"]
    assert len(corrections) == 1
    assert corrections[0]["original"] == ""
    assert corrections[0]["explanation"] == "Sorry, I can't help with that."


async def test_grammar_check_returns_503_when_all_providers_fail(client):
    headers = await _authed_headers(client)
    app.dependency_overrides[get_ai_orchestrator] = lambda: FakeAIOrchestrator(fails=True)

    resp = await client.post(
        "/api/v1/grammar/check", json={"text": "she don't like coffee"}, headers=headers
    )

    del app.dependency_overrides[get_ai_orchestrator]

    assert resp.status_code == 503


async def test_grammar_check_requires_auth(client):
    resp = await client.post("/api/v1/grammar/check", json={"text": "she don't like coffee"})
    assert resp.status_code in (401, 403)


async def test_grammar_check_rejects_empty_text(client):
    headers = await _authed_headers(client)
    resp = await client.post("/api/v1/grammar/check", json={"text": ""}, headers=headers)
    assert resp.status_code == 422
