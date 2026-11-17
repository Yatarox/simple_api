from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PhotoAlbumCreate(BaseModel):
    event_id: int
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class PhotoAlbumUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class PhotoAlbumResponse(PhotoAlbumCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PhotoCreate(BaseModel):
    album_id: int
    user_id: int
    url: str = Field(max_length=255)
    description: str | None = None


class PhotoUpdate(BaseModel):
    url: str | None = Field(default=None, max_length=255)
    description: str | None = None


class PhotoResponse(PhotoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PhotoCommentCreate(BaseModel):
    photo_id: int
    user_id: int
    content: str = Field(min_length=1)


class PhotoCommentUpdate(BaseModel):
    content: str = Field(min_length=1)


class PhotoCommentResponse(PhotoCommentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
