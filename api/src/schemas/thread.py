from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ThreadCreate(BaseModel):
    group_id: int | None = None
    event_id: int | None = None

    @model_validator(mode="after")
    def validate_parent(self):
        if (self.group_id is None) == (self.event_id is None):
            raise ValueError("Un thread doit appartenir à un groupe OU à un événement (pas les deux)")
        return self


class ThreadResponse(ThreadCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ThreadMessageCreate(BaseModel):
    thread_id: int
    user_id: int
    content: str = Field(min_length=1)
    parent_message_id: int | None = None


class MessageUpdate(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(ThreadMessageCreate):   # ✅ corrigé
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
