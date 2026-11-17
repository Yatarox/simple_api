from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketTypeCreate,
    TicketTypeResponse,
    TicketTypeUpdate,
)
from src.services.ticket_service import TicketService, TicketTypeService


router = APIRouter(
    prefix="/tickets",
    tags=["Billetterie"],
)


@router.post(
    "/types",
    response_model=TicketTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un type de billet",
    description=(
        "Crée un type de billet pour un événement. "
        "Seul un organisateur peut créer un type de billet."
    ),
)
def create_ticket_type(
    payload: TicketTypeCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        return TicketTypeService(db).create(
            user_id=current.id,
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
    "/types/{type_id}",
    response_model=TicketTypeResponse,
    summary="Modifier un type de billet",
    description="Modifie le prix ou la quantité d'un type de billet.",
)
def update_ticket_type(
    type_id: int,
    payload: TicketTypeUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ticket_type = TicketTypeService(db).update(
        type_id,
        **payload.model_dump(exclude_unset=True),
    )

    if ticket_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Type de billet introuvable",
        )

    return ticket_type


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Acheter un billet",
    description=(
        "Achète un billet pour un événement public. "
        "Un acheteur ne peut avoir qu'un seul billet par événement."
    ),
)
def buy_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
):
    try:
        return TicketService(db).create(
            **payload.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Obtenir un billet",
    description="Retourne les informations d'un billet grâce à son identifiant.",
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = TicketService(db).get(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billet introuvable",
        )

    return ticket