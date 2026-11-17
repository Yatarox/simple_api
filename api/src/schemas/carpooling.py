from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CarpoolingCreate(BaseModel):
    event_id: int
    departure_location: str
    departure_time: datetime
    price: Decimal = Field(ge=0)
    available_seats: int = Field(gt=0)
    max_detour_minutes: int = Field(default=0, ge=0)


class CarpoolingUpdate(BaseModel):
    departure_location: str | None = None
    departure_time: datetime | None = None
    price: Decimal | None = Field(default=None, ge=0)
    available_seats: int | None = Field(default=None, gt=0)
    max_detour_minutes: int | None = Field(default=None, ge=0)


class CarpoolingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    driver_id: int
    departure_location: str
    departure_time: datetime
    price: Decimal
    available_seats: int
    max_detour_minutes: int