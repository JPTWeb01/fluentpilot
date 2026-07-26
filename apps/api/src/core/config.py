from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    cors_origins: str = "http://localhost:5173"

    # AI providers — all optional. A provider is only wired into the orchestrator
    # if its API key is set, so local dev works with zero, one, or all of them.
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"
    gemini_tts_model: str = "gemini-2.5-flash-preview-tts"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Speech (STT/TTS) — reuses groq_api_key/gemini_api_key above, just different models.
    groq_stt_model: str = "whisper-large-v3"
    groq_tts_model: str = "canopylabs/orpheus-v1-english"

    # Piper — local/offline TTS-only fallback, no key needed. Voice model must be
    # downloaded separately (see services/ai README); if missing, synthesis just
    # fails like any other provider failure.
    piper_voice: str = "en_US-lessac-medium"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
