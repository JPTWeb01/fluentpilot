import pytest

from fluentpilot_ai.exceptions import AllProvidersFailedError
from fluentpilot_ai.speech.router import SpeechOrchestrator
from tests.conftest import FakeSpeechProvider


async def test_transcribe_uses_first_provider_in_chain():
    groq = FakeSpeechProvider("groq", transcript="from groq")
    gemini = FakeSpeechProvider("gemini", transcript="from gemini")
    orchestrator = SpeechOrchestrator({"groq": groq, "gemini": gemini})

    transcript = await orchestrator.transcribe(b"audio", "audio/webm")

    assert transcript == "from groq"
    assert len(groq.transcribe_calls) == 1
    assert len(gemini.transcribe_calls) == 0


async def test_transcribe_falls_back_when_primary_fails():
    groq = FakeSpeechProvider("groq", fails=True)
    gemini = FakeSpeechProvider("gemini", transcript="from gemini")
    orchestrator = SpeechOrchestrator({"groq": groq, "gemini": gemini})

    transcript = await orchestrator.transcribe(b"audio", "audio/webm")

    assert transcript == "from gemini"


async def test_transcribe_skips_unconfigured_providers():
    gemini = FakeSpeechProvider("gemini", transcript="from gemini")
    orchestrator = SpeechOrchestrator({"gemini": gemini})

    transcript = await orchestrator.transcribe(b"audio", "audio/webm")

    assert transcript == "from gemini"


async def test_transcribe_raises_when_all_providers_fail():
    groq = FakeSpeechProvider("groq", fails=True)
    gemini = FakeSpeechProvider("gemini", fails=True)
    orchestrator = SpeechOrchestrator({"groq": groq, "gemini": gemini})

    with pytest.raises(AllProvidersFailedError) as exc_info:
        await orchestrator.transcribe(b"audio", "audio/webm")

    assert set(exc_info.value.errors) == {"groq", "gemini"}


async def test_synthesize_uses_first_provider_in_chain():
    groq = FakeSpeechProvider("groq", audio_bytes=b"groq-audio")
    gemini = FakeSpeechProvider("gemini", audio_bytes=b"gemini-audio")
    orchestrator = SpeechOrchestrator({"groq": groq, "gemini": gemini})

    audio = await orchestrator.synthesize("hello")

    assert audio.audio_bytes == b"groq-audio"
    assert audio.mime_type == "audio/wav"
    assert len(groq.synthesize_calls) == 1
    assert len(gemini.synthesize_calls) == 0


async def test_synthesize_falls_back_when_primary_fails():
    groq = FakeSpeechProvider("groq", fails=True)
    gemini = FakeSpeechProvider("gemini", audio_bytes=b"gemini-audio")
    orchestrator = SpeechOrchestrator({"groq": groq, "gemini": gemini})

    audio = await orchestrator.synthesize("hello")

    assert audio.audio_bytes == b"gemini-audio"


async def test_synthesize_raises_when_all_providers_fail():
    groq = FakeSpeechProvider("groq", fails=True)
    gemini = FakeSpeechProvider("gemini", fails=True)
    orchestrator = SpeechOrchestrator({"groq": groq, "gemini": gemini})

    with pytest.raises(AllProvidersFailedError) as exc_info:
        await orchestrator.synthesize("hello")

    assert set(exc_info.value.errors) == {"groq", "gemini"}
