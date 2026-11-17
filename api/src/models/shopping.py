from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    __table_args__ = (UniqueConstraint("event_id", "name"),)   # 1 chose unique par event

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
