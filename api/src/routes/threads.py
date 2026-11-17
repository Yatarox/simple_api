from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.thread import (
    ThreadCreate,
    ThreadMessageCreate,
    ThreadResponse,
    MessageResponse,
)
from src.services.thread_service import ThreadService


router = APIRouter(
    prefix="/threads",
    tags=["Fils de discussion"],
)


@router.post(
    "",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un fil de discussion",
    description="Crée un fil lié à un groupe ou à un événement.",
)
def create_thread(
    payload: ThreadCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        return ThreadService(db).create(
            group_id=payload.group_id,
            event_id=payload.event_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.get(
    "/{thread_id}",
    response_model=ThreadResponse,
    summary="Obtenir un fil de discussion",
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
):
    thread = ThreadService(db).get(thread_id)

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fil de discussion introuvable",
        )

    return thread


@router.get(
    "/{thread_id}/messages",
    response_model=list[MessageResponse],
    summary="Lister les messages",
)
def list_messages(
    thread_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = ThreadService(db)

    if service.get(thread_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fil de discussion introuvable",
        )

    return service.get_messages(thread_id, skip, limit)


@router.post(
    "/{thread_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Publier un message",
    description="Publie un message dans un fil de discussion.",
)
def post_message(
    thread_id: int,
    payload: ThreadMessageCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = ThreadService(db)

    if service.get(thread_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fil de discussion introuvable",
        )

    try:
        return service.add_message(
            thread_id=thread_id,
            user_id=current.id,
            content=payload.content,
            parent_message_id=payload.parent_message_id,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )