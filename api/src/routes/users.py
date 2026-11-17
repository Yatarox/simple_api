from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.user import UserResponse, UserUpdate
from src.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"],
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtenir son profil",
    description="Retourne les informations de l'utilisateur connecté.",
)
def get_me(
    current: User = Depends(get_current_user),
):
    return current


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtenir un utilisateur",
    description="Retourne les informations publiques d'un utilisateur.",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = UserService(db).get(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable",
        )

    return user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Modifier son profil",
    description="Modifie les informations de l'utilisateur connecté.",
)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        user = UserService(db).update(
            current.id,
            **payload.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable",
        )

    return user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer son compte",
    description="Supprime définitivement le compte de l'utilisateur connecté.",
)
def delete_me(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    deleted = UserService(db).delete(current.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable",
        )