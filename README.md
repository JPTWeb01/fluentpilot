# FluentPilot (SpeakFlow AI)

A voice-first AI English speaking coach. Real-time conversation practice with grammar correction,
pronunciation feedback, vocabulary coaching, and interview/workplace communication training — built
as a modular monolith designed to scale into independent services.

## Status

Phase 1 (Foundation) in progress: monorepo scaffold, containerized Postgres/Redis, FastAPI backend,
JWT authentication.

## Stack

| Layer            | Technology |
|-------------------|------------|
| Web               | React, TypeScript, Vite, Tailwind, shadcn/ui, Zustand, TanStack Query |
| Mobile            | React Native, Expo, TypeScript |
| API               | Python, FastAPI, SQLAlchemy (async), Alembic, Pydantic |
| Database          | PostgreSQL |
| Cache             | Redis |
| Background jobs   | Celery |
| Storage           | Supabase Storage |
| Auth              | JWT (access + rotating refresh tokens), OAuth-ready |
| AI                | Groq (primary) → Gemini (secondary) → Ollama (fallback), behind a provider-agnostic orchestrator |

## Monorepo layout

```
apps/
  web/       React web app
  mobile/    Expo mobile app
  api/       FastAPI backend
packages/
  shared/    Shared types/config across apps
services/
  ai/        AI orchestrator + provider adapters (Groq / Gemini / Ollama)
infra/
  docker/    Docker Compose for local dev
docs/        Architecture and design notes
```

## Local development — API

```bash
cd apps/api
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env   # fill in real secrets
alembic upgrade head
uvicorn src.main:app --reload
```

Or via Docker Compose (brings up Postgres + Redis + API):

```bash
copy .env.example .env
docker compose -f infra/docker/docker-compose.yml up --build
```

Run tests (no external services required — uses an in-memory SQLite DB):

```bash
cd apps/api
pytest
```

## Roadmap

1. **Foundation** — monorepo, Docker, FastAPI, PostgreSQL, JWT auth
2. **AI Foundation** — provider-agnostic AI orchestrator (Groq / Gemini / Ollama)
3. **Voice System** — STT/TTS real-time conversation pipeline
4. **English Coach Modules** — grammar, vocabulary, pronunciation, accent, interview, workplace
5. **Mobile App** — Expo client
6. **Production Optimization** — caching, rate limiting, cost monitoring, deployment hardening
