from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.ticket import (TicketTypeCreate, TicketTypeUpdate, TicketTypeResponse,
                                TicketCreate, TicketResponse)
from src.services.ticket_service import TicketTypeService, TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/types", response_model=TicketTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_type(payload: TicketTypeCreate, db: Session = Depends(get_db),
                       current: User = Depends(get_current_user)):
    data = payload.model_dump()
    return TicketTypeService(db).create(user_id=current.id, **data)


@router.patch("/types/{type_id}", response_model=TicketTypeResponse)
def update_ticket_type(type_id: int, payload: TicketTypeUpdate,
                       db: Session = Depends(get_db),
                       current: User = Depends(get_current_user)):
    t = TicketTypeService(db).update(type_id, **payload.model_dump(exclude_unset=True))
    if not t:
        raise HTTPException(status_code=404, detail="Type de billet introuvable")
    return t


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def buy_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    return TicketService(db).create(**payload.model_dump())


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    t = TicketService(db).get(ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Billet introuvable")
    return t
