from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class Carpooling(Base):
    __tablename__ = "carpoolings"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    departure_location: Mapped[str] = mapped_column(String(255), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    max_detour_minutes: Mapped[int] = mapped_column(Integer, default=0)
