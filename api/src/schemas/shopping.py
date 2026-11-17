from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ShoppingItemCreate(BaseModel):
    event_id: int
    user_id: int
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(gt=0)
    arrival_time: datetime


class ShoppingItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    quantity: int | None = Field(default=None, gt=0)
    arrival_time: datetime | None = None


class ShoppingItemResponse(ShoppingItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
