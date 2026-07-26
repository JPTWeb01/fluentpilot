from pydantic import BaseModel, Field

MAX_TEXT_LENGTH = 5_000


class PronunciationCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class PronunciationTip(BaseModel):
    word: str
    tip: str


class PronunciationCheckResponse(BaseModel):
    tips: list[PronunciationTip]
