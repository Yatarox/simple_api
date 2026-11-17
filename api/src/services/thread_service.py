from sqlalchemy.orm import Session
from src.models.thread import Thread, Message
from src.models.group import GroupMember
from src.models.event import EventOrganizer, EventParticipant
from src.services.base_service import BaseService


class ThreadService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Thread)

    def create(self, *, group_id: int | None = None, event_id: int | None = None) -> Thread:
        if (group_id is None) == (event_id is None):
            raise ValueError("Un thread doit être lié à un groupe OU à un événement")
        return super().create(group_id=group_id, event_id=event_id)

    def get_messages(self, thread_id: int, skip=0, limit=100) -> list[Message]:
        return (
            self.db.query(Message)
            .filter(Message.thread_id == thread_id)
            .order_by(Message.created_at.asc())
            .offset(skip).limit(limit).all()
        )

    def _can_post(self, thread: Thread, user_id: int) -> bool:
        if thread.group_id is not None:
            member = (
                self.db.query(GroupMember)
                .filter(GroupMember.group_id == thread.group_id,
                        GroupMember.user_id == user_id)
                .first()
            )
            return member is not None
        organizer = (
            self.db.query(EventOrganizer)
            .filter(EventOrganizer.event_id == thread.event_id,
                    EventOrganizer.user_id == user_id)
            .first()
        )
        participant = (
            self.db.query(EventParticipant)
            .filter(EventParticipant.event_id == thread.event_id,
                    EventParticipant.user_id == user_id)
            .first()
        )
        return organizer is not None or participant is not None

    def add_message(self, *, thread_id: int, user_id: int, content: str,
                    parent_message_id: int | None = None) -> Message:
        thread = self.get(thread_id)
        if thread is None:
            raise ValueError("Thread introuvable")
        if not self._can_post(thread, user_id):
            raise PermissionError("Vous n'êtes pas autorisé à publier dans ce thread")
        m = Message(thread_id=thread_id, user_id=user_id, content=content,
                    parent_message_id=parent_message_id)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return m
