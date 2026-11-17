from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class Group(Base):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon_url: Mapped[str | None] = mapped_column(String(255))
    picture_url: Mapped[str | None] = mapped_column(String(255))
    visibility: Mapped[str] = mapped_column(Enum("public", "private", "secret"), default="public")
    members_can_publish: Mapped[bool] = mapped_column(Boolean, default=False)
    members_can_create_events: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("user_groups.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(Enum("member", "admin"), default="member")
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
