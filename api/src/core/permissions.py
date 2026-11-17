from sqlalchemy.orm import Session
from src.models.event import EventOrganizer, EventParticipant
from src.models.group import GroupMember


def is_event_organizer(db: Session, user_id: int, event_id: int) -> bool:
    return (
        db.query(EventOrganizer)
        .filter(EventOrganizer.event_id == event_id, EventOrganizer.user_id == user_id)
        .first()
    ) is not None


def is_event_participant(db: Session, user_id: int, event_id: int) -> bool:
    return (
        db.query(EventParticipant)
        .filter(EventParticipant.event_id == event_id, EventParticipant.user_id == user_id)
        .first()
    ) is not None


def is_group_admin(db: Session, user_id: int, group_id: int) -> bool:
    return (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.role == "admin")
        .first()
    ) is not None


def is_group_member(db: Session, user_id: int, group_id: int) -> bool:
    return (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        .first()
    ) is not None
