# ADR-0001: Voice System v1 scope

## Status

Accepted

## Context

Phase 3 of the roadmap introduces voice conversation: the user speaks to the app and
gets a spoken reply back. Three scope decisions were made up front to keep v1 shippable.

## Decisions

**Turn-based (push-to-talk), not real-time streaming.** The browser records a whole
utterance, uploads it, and gets back transcript + reply text + reply audio in one
response. True duplex streaming would need a streaming STT provider (Groq's Whisper API
is request/response, not streaming) and net-new WebSocket infrastructure that doesn't
exist anywhere in this repo yet.

**Groq primary, Gemini fallback for both STT and TTS.** Mirrors the existing
`AIOrchestrator` text-chat fallback pattern (`services/ai`). No Ollama — it has no
local STT/TTS capability.

**Stateless v1 — no DB persistence.** The frontend holds conversation history in memory
and resends it each turn, the same shape as the `AIMessage` history already used by
text chat.

## Deferred (fast-follows, not v1-blocking)

- Persisting voice conversations to the database.
- Real-time/streaming voice (duplex audio, WebSocket transport).
- Usage tracking for speech (audio seconds/characters) — the existing `UsageRecorder`
  is token-based and doesn't fit STT/TTS billing units.
- A hard server-side request body size limit (v1 only has a `Field(max_length=...)`
  guard on the base64 payload).
