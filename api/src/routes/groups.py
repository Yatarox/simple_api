from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.permissions import is_group_admin
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.group import (
    GroupCreate,
    GroupMemberCreate,
    GroupMemberResponse,
    GroupResponse,
    GroupUpdate,
)
from src.services.group_service import GroupService


router = APIRouter(
    prefix="/groups",
    tags=["Groupes"],
)


@router.get(
    "",
    response_model=list[GroupResponse],
    summary="Lister les groupes",
    description="Retourne la liste des groupes disponibles.",
)
def list_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return GroupService(db).list(skip, limit)


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Obtenir un groupe",
    description="Retourne les informations d'un groupe grâce à son identifiant.",
)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    group = GroupService(db).get(group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe introuvable",
        )

    return group


@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un groupe",
    description=(
        "Crée un groupe. "
        "L'utilisateur connecté devient automatiquement administrateur."
    ),
)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        return GroupService(db).create(
            creator_id=current.id,
            **payload.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.patch(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Modifier un groupe",
    description="Modifie un groupe. Seul un administrateur peut le modifier.",
)
def update_group(
    group_id: int,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not is_group_admin(db, current.id, group_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas administrateur de ce groupe",
        )

    group = GroupService(db).update(
        group_id,
        **payload.model_dump(exclude_unset=True),
    )

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe introuvable",
        )

    return group


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un groupe",
    description="Supprime un groupe. Seul un administrateur peut le supprimer.",
)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not is_group_admin(db, current.id, group_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas administrateur de ce groupe",
        )

    deleted = GroupService(db).delete(group_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe introuvable",
        )


@router.get(
    "/{group_id}/members",
    response_model=list[GroupMemberResponse],
    summary="Lister les membres",
    description="Retourne tous les membres d'un groupe.",
)
def list_members(
    group_id: int,
    db: Session = Depends(get_db),
):
    return GroupService(db).get_members(group_id)


@router.post(
    "/{group_id}/members",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un membre",
    description="Ajoute un utilisateur à un groupe. Seul un administrateur peut l'ajouter.",
)
def add_member(
    group_id: int,
    payload: GroupMemberCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not is_group_admin(db, current.id, group_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas administrateur de ce groupe",
        )

    try:
        return GroupService(db).add_member(
            group_id=group_id,
            user_id=payload.user_id,
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )