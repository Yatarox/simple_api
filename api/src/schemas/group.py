from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    icon_url: str | None = Field(default=None, max_length=255)
    picture_url: str | None = Field(default=None, max_length=255)
    visibility: Literal["public", "private", "secret"] = "public"
    members_can_publish: bool = False
    members_can_create_events: bool = False


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    icon_url: str | None = Field(default=None, max_length=255)
    picture_url: str | None = Field(default=None, max_length=255)
    visibility: Literal["public", "private", "secret"] | None = None
    members_can_publish: bool | None = None
    members_can_create_events: bool | None = None


class GroupResponse(GroupCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class GroupMemberCreate(BaseModel):
    group_id: int
    user_id: int
    role: Literal["member", "admin"] = "member"


class GroupMemberResponse(GroupMemberCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    joined_at: datetime
