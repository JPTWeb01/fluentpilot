from pydantic import BaseModel, Field

# A single spoken utterance won't realistically exceed this.
MAX_TEXT_LENGTH = 5_000


class GrammarCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class GrammarCorrection(BaseModel):
    original: str
    corrected: str
    explanation: str


class GrammarCheckResponse(BaseModel):
    corrections: list[GrammarCorrection]
