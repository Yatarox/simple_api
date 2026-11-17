from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class TicketType(Base):
    __tablename__ = "ticket_types"
    __table_args__ = (UniqueConstraint("id", "event_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (UniqueConstraint("event_id", "email"),)   # 1 billet / personne / event

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    ticket_type_id: Mapped[int] = mapped_column(ForeignKey("ticket_types.id", ondelete="CASCADE"))
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    purchase_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
