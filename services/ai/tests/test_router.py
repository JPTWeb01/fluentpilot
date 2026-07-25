import pytest

from fluentpilot_ai.exceptions import AllProvidersFailedError
from fluentpilot_ai.router import AIOrchestrator
from tests.conftest import FakeProvider


async def test_uses_first_provider_in_chain(make_request):
    groq = FakeProvider("groq", reply="from groq")
    gemini = FakeProvider("gemini", reply="from gemini")
    orchestrator = AIOrchestrator({"groq": groq, "gemini": gemini})

    response = await orchestrator.complete(make_request("conversation"))

    assert response.content == "from groq"
    assert len(groq.calls) == 1
    assert len(gemini.calls) == 0


async def test_falls_back_when_primary_fails(make_request):
    groq = FakeProvider("groq", fails=True)
    gemini = FakeProvider("gemini", reply="from gemini")
    orchestrator = AIOrchestrator({"groq": groq, "gemini": gemini})

    response = await orchestrator.complete(make_request("conversation"))

    assert response.content == "from gemini"


async def test_complex_task_prefers_gemini_first(make_request):
    groq = FakeProvider("groq", reply="from groq")
    gemini = FakeProvider("gemini", reply="from gemini")
    orchestrator = AIOrchestrator({"groq": groq, "gemini": gemini})

    response = await orchestrator.complete(make_request("interview_prep"))

    assert response.content == "from gemini"
    assert len(groq.calls) == 0


async def test_skips_unconfigured_providers(make_request):
    gemini = FakeProvider("gemini", reply="from gemini")
    orchestrator = AIOrchestrator({"gemini": gemini})

    response = await orchestrator.complete(make_request("conversation"))

    assert response.content == "from gemini"


async def test_raises_when_all_providers_fail(make_request):
    groq = FakeProvider("groq", fails=True)
    gemini = FakeProvider("gemini", fails=True)
    ollama = FakeProvider("ollama", fails=True)
    orchestrator = AIOrchestrator({"groq": groq, "gemini": gemini, "ollama": ollama})

    with pytest.raises(AllProvidersFailedError) as exc_info:
        await orchestrator.complete(make_request("conversation"))

    assert set(exc_info.value.errors) == {"groq", "gemini", "ollama"}


async def test_unknown_task_uses_default_chain(make_request):
    groq = FakeProvider("groq", reply="from groq")
    orchestrator = AIOrchestrator({"groq": groq})

    response = await orchestrator.complete(make_request("some_future_task"))

    assert response.content == "from groq"
