from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TicketTypeCreate(BaseModel):
    event_id: int
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(ge=0)
    quantity: int = Field(ge=0)


class TicketTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)


class TicketTypeResponse(TicketTypeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TicketCreate(BaseModel):
    event_id: int
    ticket_type_id: int
    last_name: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    address: str = Field(min_length=1, max_length=255)
    postal_code: str = Field(min_length=1, max_length=20)
    city: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)


class TicketResponse(TicketCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    purchase_date: datetime
