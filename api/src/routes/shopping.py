from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.shopping import (
    ShoppingItemCreate,
    ShoppingItemResponse,
    ShoppingItemUpdate,
)
from src.services.shopping_service import ShoppingService


router = APIRouter(
    prefix="/shopping",
    tags=["Liste de courses"],
)


@router.get(
    "",
    response_model=list[ShoppingItemResponse],
    summary="Lister les articles",
    description="Retourne tous les articles de la liste de courses d'un événement.",
)
def list_items(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return ShoppingService(db).list_by_event(
        event_id,
        skip,
        limit,
    )


@router.post(
    "",
    response_model=ShoppingItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un article",
    description=(
        "Ajoute un article à la liste de courses. "
        "L'utilisateur connecté devient responsable de l'article."
    ),
)
def create_item(
    payload: ShoppingItemCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    data = payload.model_dump()
    data.pop("user_id", None)

    try:
        return ShoppingService(db).create(
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
    "/{item_id}",
    response_model=ShoppingItemResponse,
    summary="Modifier un article",
    description="Modifie un article de la liste de courses.",
)
def update_item(
    item_id: int,
    payload: ShoppingItemUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = ShoppingService(db)
    item = service.get(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article introuvable",
        )

    if item.user_id != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas responsable de cet article",
        )

    try:
        return service.update(
            item_id,
            **payload.model_dump(exclude_unset=True),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un article",
    description="Supprime un article de la liste de courses.",
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = ShoppingService(db)
    item = service.get(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article introuvable",
        )

    if item.user_id != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas responsable de cet article",
        )

    service.delete(item_id)