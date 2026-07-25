from dataclasses import dataclass
from typing import Literal

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class AIMessage:
    role: Role
    content: str


@dataclass(frozen=True, slots=True)
class AIRequest:
    messages: list[AIMessage]
    task: str
    temperature: float = 0.7
    max_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class TokenUsage:
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True, slots=True)
class AIResponse:
    content: str
    usage: TokenUsage
    latency_ms: float
