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
