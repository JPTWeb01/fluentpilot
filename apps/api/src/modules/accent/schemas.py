from pydantic import BaseModel, Field

MAX_TEXT_LENGTH = 5_000


class AccentCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class AccentTip(BaseModel):
    phrase: str
    tip: str


class AccentCheckResponse(BaseModel):
    tips: list[AccentTip]
