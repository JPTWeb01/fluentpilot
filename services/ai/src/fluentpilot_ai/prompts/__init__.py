from functools import cache
from importlib import resources


@cache
def load_prompt(name: str) -> str:
    """Load a packaged system-prompt template by name (without the .txt suffix)."""
    path = resources.files("fluentpilot_ai.prompts").joinpath(f"{name}.txt")
    return path.read_text(encoding="utf-8").strip()
