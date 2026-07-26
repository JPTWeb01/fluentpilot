from pydantic import BaseModel, Field

# A single spoken utterance won't realistically exceed this.
MAX_TEXT_LENGTH = 5_000


class VocabularyCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class VocabularySuggestion(BaseModel):
    original: str
    suggestion: str
    explanation: str


class VocabularyCheckResponse(BaseModel):
    suggestions: list[VocabularySuggestion]
