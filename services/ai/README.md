# services/ai — `fluentpilot-ai`

AI orchestrator and provider adapters. Installed by `apps/api` as an editable local
package (`-e ../../services/ai`) so it can later be extracted into its own service
without changing its internal API.

## Architecture

`AIOrchestrator.complete(request)` never talks to a provider SDK directly — it routes
through the `AIProvider` interface and a per-task fallback chain:

- **Simple/quick tasks** (conversation, grammar, vocabulary, pronunciation):
  Groq → Gemini → Ollama
- **Complex tasks** (interview_prep, lesson_generation, progress_analysis):
  Gemini → Groq → Ollama

A provider raises `ProviderError` (or a subclass — `ProviderTimeoutError`,
`ProviderRateLimitError`, `ProviderAPIError`) on failure; the orchestrator catches
only that hierarchy and moves to the next provider in the chain. Anything else is a
real bug and propagates normally. If every provider in the chain fails (or none are
configured), `AllProvidersFailedError` is raised with the per-provider errors attached.

Providers are only added to the orchestrator if configured (e.g. an API key is set) —
see `apps/api/src/core/ai.py` for how `apps/api` composes this from `Settings`.

`SpeechOrchestrator` (`speech/router.py`) follows the same shape for speech:
`transcribe()` tries Groq (Whisper STT) then falls back to Gemini (multimodal
transcription) — never Ollama or Piper (neither has STT). `synthesize()` tries Groq
(Orpheus TTS) → Gemini (native TTS) → Piper (local ONNX model, fully offline, no
API key or quota — see "Piper setup" below). `synthesize()` always returns
`SpeechAudio` with `mime_type="audio/wav"` regardless of provider — Gemini's native
audio output is raw PCM and Piper's is raw int16 PCM chunks, so both adapters wrap
their output in a WAV header before returning, keeping the format uniform for callers.

### Rate-limit reporting

Groq's REST responses carry `x-ratelimit-*` headers, parsed by
`parse_rate_limit_headers()` into a `RateLimitSnapshot` after every call — this is a
real read of the provider's own quota state. Gemini's API reports none of this, on
success or on a 429 (confirmed by inspecting a live 429 response's headers — nothing
resembling a rate-limit field is present). For Gemini TTS specifically, `rate_limit.py`
also has `DailyRequestCounter`: a self-tracked, in-process count against Gemini's
empirically-observed (not documented) 10-requests/day free-tier cap on
`gemini-2.5-flash-preview-tts`, reset at UTC midnight. It's an approximation — it
undercounts after a process restart and can drift from Google's actual reset time,
which isn't published. Gemini chat/STT have no similarly-confirmed limit, so they're
left unreported (`None`) rather than guessing a number.

### Piper setup

Piper is TTS-only and runs fully in-process (no daemon, no network) — but its ONNX
voice model isn't committed to the repo (~60MB binary) and must be downloaded once:

```
python -m piper.download_voices en_US-lessac-medium --download-dir services/ai/models/piper
```

If the model file is missing, `PiperSpeechProvider.synthesize()` raises
`ProviderAPIError` (with the download command in the message) — same fail-soft
behavior as any other provider being unconfigured, so the app still runs, it just
has one fewer TTS fallback. Voice is configurable via `PIPER_VOICE` (see
`apps/api/src/core/config.py`), and must match a filename already downloaded into
`services/ai/models/piper/`.

## Layout

```
services/ai/
├── pyproject.toml
├── src/fluentpilot_ai/
│   ├── types.py               # AIMessage, AIRequest, AIResponse, TokenUsage
│   ├── exceptions.py          # ProviderError hierarchy, AllProvidersFailedError
│   ├── provider_interface.py  # AIProvider abstract base
│   ├── usage.py                # UsageRecorder protocol + LoggingUsageRecorder
│   ├── router.py               # AIOrchestrator + task fallback chains
│   ├── providers/
│   │   ├── groq_provider.py
│   │   ├── gemini_provider.py
│   │   └── ollama_provider.py
│   ├── speech/                  # SpeechOrchestrator + STT/TTS provider adapters
│   │   ├── types.py              # SpeechAudio
│   │   ├── provider_interface.py # SpeechToTextProvider, TextToSpeechProvider
│   │   ├── router.py             # SpeechOrchestrator + STT/TTS fallback chains
│   │   └── providers/
│   │       ├── groq_speech_provider.py
│   │       ├── gemini_speech_provider.py
│   │       └── piper_speech_provider.py
│   └── prompts/                # packaged system-prompt templates + loader
│       ├── conversation.txt
│       ├── grammar.txt
│       ├── pronunciation.txt
│       ├── accent.txt
│       └── interview.txt
├── tests/                      # fallback logic, tested against fake providers
└── scripts/smoke_test.py       # manual, hits real provider APIs — needs API keys
```

## Testing

```
pip install -e .[dev]
pytest
```

The automated suite uses fake providers only — no API key or network access required.
To verify against real provider APIs:

```
GROQ_API_KEY=... GEMINI_API_KEY=... python scripts/smoke_test.py
```
