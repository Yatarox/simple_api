from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PollCreate(BaseModel):
    event_id: int
    created_by: int
    title: str = Field(min_length=1, max_length=255)


class PollUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)


class PollResponse(PollCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PollQuestionCreate(BaseModel):
    poll_id: int
    question: str = Field(min_length=1)


class PollQuestionUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=1)


class PollQuestionResponse(PollQuestionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PollOptionCreate(BaseModel):
    question_id: int
    option_text: str = Field(min_length=1, max_length=255)


class PollOptionUpdate(BaseModel):
    option_text: str | None = Field(default=None, min_length=1, max_length=255)


class PollOptionResponse(PollOptionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PollAnswerCreate(BaseModel):
    question_id: int
    option_id: int
    user_id: int


class PollAnswerResponse(PollAnswerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
