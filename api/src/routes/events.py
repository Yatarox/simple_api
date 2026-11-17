from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.permissions import is_event_organizer
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.event import (
    EventCreate,
    EventParticipantCreate,
    EventParticipantResponse,
    EventResponse,
    EventUpdate,
)
from src.services.event_service import EventService


router = APIRouter(
    prefix="/events",
    tags=["Événements"],
)


@router.get(
    "",
    response_model=list[EventResponse],
    summary="Lister les événements",
    description="Retourne la liste des événements, avec filtrage optionnel par groupe.",
)
def list_events(
    group_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = EventService(db)

    if group_id is not None:
        return service.list_by_group(group_id, skip, limit)

    return service.list(skip, limit)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Obtenir un événement",
    description="Retourne les détails d'un événement grâce à son identifiant.",
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = EventService(db).get(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement introuvable",
        )

    return event


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un événement",
    description=(
        "Crée un événement. "
        "L'utilisateur connecté devient automatiquement son organisateur."
    ),
)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    data = payload.model_dump()
    data.pop("created_by", None)

    try:
        return EventService(db).create(
            creator_id=current.id,
            **data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.patch(
    "/{event_id}",
    response_model=EventResponse,
    summary="Modifier un événement",
    description="Modifie un événement. Seul un organisateur peut le modifier.",
)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not is_event_organizer(db, current.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas organisateur de cet événement",
        )

    try:
        event = EventService(db).update(
            event_id,
            **payload.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement introuvable",
        )

    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un événement",
    description="Supprime un événement. Seul un organisateur peut le supprimer.",
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not is_event_organizer(db, current.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas organisateur de cet événement",
        )

    deleted = EventService(db).delete(event_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement introuvable",
        )


@router.post(
    "/{event_id}/participants",
    response_model=EventParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un participant",
    description="Ajoute un utilisateur à la liste des participants d'un événement.",
)
def add_participant(
    event_id: int,
    payload: EventParticipantCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        return EventService(db).add_participant(
            event_id=event_id,
            user_id=payload.user_id,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )