# services/ai

Reserved for the AI orchestrator and provider adapters (Groq → Gemini → Ollama), built in Phase 2.

Planned layout:

```
services/ai/
├── router.py
├── provider_interface.py
├── providers/
│   ├── groq.py
│   ├── gemini.py
│   └── ollama.py
└── prompts/
    ├── conversation.txt
    ├── grammar.txt
    ├── pronunciation.txt
    ├── accent.txt
    └── interview.txt
```
