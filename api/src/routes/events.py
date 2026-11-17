from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.permissions import is_event_organizer
from src.models.users import User
from src.schemas.event import (EventCreate, EventUpdate, EventResponse,
                               EventParticipantCreate, EventParticipantResponse)
from src.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def list_events(group_id: int | None = None, skip: int = 0, limit: int = 100,
                db: Session = Depends(get_db)):
    service = EventService(db)
    if group_id is not None:
        return service.list_by_group(group_id, skip, limit)
    return service.list(skip, limit)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    e = EventService(db).get(event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return e


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("created_by", None)
    return EventService(db).create(creator_id=current.id, **data)


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    if not is_event_organizer(db, current.id, event_id):
        raise HTTPException(status_code=403, detail="Non autorisé")
    e = EventService(db).update(event_id, **payload.model_dump(exclude_unset=True))
    if not e:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return e


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    if not is_event_organizer(db, current.id, event_id):
        raise HTTPException(status_code=403, detail="Non autorisé")
    if not EventService(db).delete(event_id):
        raise HTTPException(status_code=404, detail="Événement introuvable")


@router.post("/{event_id}/participants", response_model=EventParticipantResponse,
             status_code=status.HTTP_201_CREATED)
def add_participant(event_id: int, payload: EventParticipantCreate,
                    db: Session = Depends(get_db),
                    current: User = Depends(get_current_user)):
    return EventService(db).add_participant(event_id, payload.user_id, payload.status)
