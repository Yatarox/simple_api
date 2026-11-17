from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.carpooling import (
    CarpoolingCreate,
    CarpoolingResponse,
    CarpoolingUpdate,
)
from src.services.carpooling_service import CarpoolingService


router = APIRouter(
    prefix="/carpoolings",
    tags=["Covoiturage"],
)


@router.get(
    "",
    response_model=list[CarpoolingResponse],
    summary="Lister les covoiturages",
    description="Retourne tous les covoiturages disponibles pour un événement.",
)
def list_carpoolings(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return CarpoolingService(db).list_by_event(
        event_id,
        skip,
        limit,
    )


@router.get(
    "/{carpooling_id}",
    response_model=CarpoolingResponse,
    summary="Obtenir un covoiturage",
    description="Retourne les détails d'un covoiturage grâce à son identifiant.",
)
def get_carpooling(
    carpooling_id: int,
    db: Session = Depends(get_db),
):
    carpooling = CarpoolingService(db).get(carpooling_id)

    if carpooling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covoiturage introuvable",
        )

    return carpooling


@router.post(
    "",
    response_model=CarpoolingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un covoiturage",
    description=(
        "Crée une proposition de covoiturage. "
        "Le conducteur est automatiquement défini avec l'utilisateur connecté."
    ),
)
def create_carpooling(
    payload: CarpoolingCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        return CarpoolingService(db).create(
            driver_id=current.id,
            **payload.model_dump(),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.patch(
    "/{carpooling_id}",
    response_model=CarpoolingResponse,
    summary="Modifier un covoiturage",
    description=(
        "Modifie un covoiturage. "
        "Seul le conducteur ayant créé le covoiturage peut le modifier."
    ),
)
def update_carpooling(
    carpooling_id: int,
    payload: CarpoolingUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = CarpoolingService(db)
    carpooling = service.get(carpooling_id)

    if carpooling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covoiturage introuvable",
        )

    if carpooling.driver_id != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas le conducteur de ce covoiturage",
        )

    try:
        return service.update(
            carpooling_id,
            **payload.model_dump(exclude_unset=True),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.delete(
    "/{carpooling_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un covoiturage",
    description=(
        "Supprime un covoiturage. "
        "Seul le conducteur ayant créé le covoiturage peut le supprimer."
    ),
)
def delete_carpooling(
    carpooling_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = CarpoolingService(db)
    carpooling = service.get(carpooling_id)

    if carpooling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covoiturage introuvable",
        )

    if carpooling.driver_id != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas le conducteur de ce covoiturage",
        )

    service.delete(carpooling_id)