from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PollQuestion(Base):
    __tablename__ = "poll_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text, nullable=False)


class PollOption(Base):
    __tablename__ = "poll_options"
    __table_args__ = (UniqueConstraint("id", "question_id"),)   # pour la FK composite

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("poll_questions.id", ondelete="CASCADE"))
    option_text: Mapped[str] = mapped_column(String(255), nullable=False)


class PollAnswer(Base):
    __tablename__ = "poll_answers"
    __table_args__ = (UniqueConstraint("question_id", "user_id"),)   # 1 réponse / question / user

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("poll_questions.id", ondelete="CASCADE"))
    option_id: Mapped[int] = mapped_column(ForeignKey("poll_options.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
