from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.photo import (
    PhotoAlbumCreate,
    PhotoAlbumResponse,
    PhotoCommentCreate,
    PhotoCommentResponse,
    PhotoCreate,
    PhotoResponse,
    PhotoUpdate,
)
from src.services.photo_service import (
    PhotoAlbumService,
    PhotoCommentService,
    PhotoService,
)


router = APIRouter(
    prefix="/photos",
    tags=["Photos"],
)


@router.post(
    "/albums",
    response_model=PhotoAlbumResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un album photo",
    description="Crée un album photo associé à un événement.",
)
def create_album(
    payload: PhotoAlbumCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return PhotoAlbumService(db).create(**payload.model_dump())


@router.get(
    "/albums/{album_id}",
    response_model=PhotoAlbumResponse,
    summary="Obtenir un album photo",
    description="Retourne les informations d'un album photo.",
)
def get_album(
    album_id: int,
    db: Session = Depends(get_db),
):
    album = PhotoAlbumService(db).get(album_id)

    if album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album introuvable",
        )

    return album


@router.post(
    "",
    response_model=PhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une photo",
    description=(
        "Ajoute une photo dans un album. "
        "Seul un participant à l'événement peut publier une photo."
    ),
)
def create_photo(
    payload: PhotoCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    data = payload.model_dump()
    data.pop("user_id", None)

    try:
        return PhotoService(db).create(
            user_id=current.id,
            **data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.patch(
    "/{photo_id}",
    response_model=PhotoResponse,
    summary="Modifier une photo",
    description="Modifie une photo. Seul son auteur peut la modifier.",
)
def update_photo(
    photo_id: int,
    payload: PhotoUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = PhotoService(db)
    photo = service.get(photo_id)

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo introuvable",
        )

    if photo.user_id != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas l'auteur de cette photo",
        )

    return service.update(
        photo_id,
        **payload.model_dump(exclude_unset=True),
    )


@router.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une photo",
    description="Supprime une photo. Seul son auteur peut la supprimer.",
)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = PhotoService(db)
    photo = service.get(photo_id)

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo introuvable",
        )

    if photo.user_id != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas l'auteur de cette photo",
        )

    service.delete(photo_id)


@router.post(
    "/{photo_id}/comments",
    response_model=PhotoCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Commenter une photo",
    description="Ajoute un commentaire sur une photo.",
)
def comment_photo(
    photo_id: int,
    payload: PhotoCommentCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        return PhotoCommentService(db).create(
            photo_id=photo_id,
            user_id=current.id,
            content=payload.content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )