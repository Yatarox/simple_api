from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    start_time: datetime
    end_time: datetime
    picture_url: str | None = Field(default=None, max_length=255)
    visibility: Literal["public", "private"] = "public"
    group_id: int | None = None
    created_by: int
    shopping_list_enabled: bool = False
    carpooling_enabled: bool = False
    ticketing_enabled: bool = False

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time doit être strictement après start_time")
        return self


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    start_time: datetime | None = None
    end_time: datetime | None = None
    picture_url: str | None = Field(default=None, max_length=255)
    visibility: Literal["public", "private"] | None = None
    group_id: int | None = None
    shopping_list_enabled: bool | None = None
    carpooling_enabled: bool | None = None
    ticketing_enabled: bool | None = None


class EventResponse(EventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EventParticipantCreate(BaseModel):
    event_id: int
    user_id: int
    status: Literal["invited", "attending", "not_attending"] = "invited"


class EventParticipantResponse(EventParticipantCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


# utile pour les organisateurs
class EventOrganizerCreate(BaseModel):
    event_id: int
    user_id: int


class EventOrganizerResponse(EventOrganizerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
