from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.event import Event, EventOrganizer, EventParticipant
from src.models.group import GroupMember
from src.services.base_service import BaseService


class EventService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Event)

    def create(self, *, creator_id: int, **data) -> Event:
        self._validate_dates(data.get("start_time"), data.get("end_time"))
        event = Event(created_by=creator_id, **data)
        self.db.add(event)
        self.db.flush()
        self.db.add(EventOrganizer(event_id=event.id, user_id=creator_id))
        if event.group_id is not None:
            members = (
                self.db.query(GroupMember)
                .filter(GroupMember.group_id == event.group_id)
                .all()
            )
            for member in members:
                self.db.add(EventParticipant(
                    event_id=event.id,
                    user_id=member.user_id,
                    status="invited",
                ))
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Événement invalide")
        self.db.refresh(event)
        return event

    def update(self, id: int, **data) -> Event | None:
        event = self.get(id)
        if event is None:
            return None
        start = data.get("start_time", event.start_time)
        end = data.get("end_time", event.end_time)
        self._validate_dates(start, end)
        return super().update(id, **data)

    @staticmethod
    def _validate_dates(start, end):
        if start is not None and end is not None and end <= start:
            raise ValueError("end_time doit être après start_time")

    def list_by_group(self, group_id: int, skip=0, limit=100):
        return self.list(skip, limit, group_id=group_id)

    def add_participant(self, event_id: int, user_id: int, status: str = "invited") -> EventParticipant:
        p = EventParticipant(event_id=event_id, user_id=user_id, status=status)
        self.db.add(p)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Participant déjà inscrit")
        self.db.refresh(p)
        return p
