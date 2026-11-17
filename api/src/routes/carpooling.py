from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.carpooling import CarpoolingCreate, CarpoolingUpdate, CarpoolingResponse
from src.services.carpooling_service import CarpoolingService

router = APIRouter(prefix="/carpoolings", tags=["carpoolings"])


@router.get("", response_model=list[CarpoolingResponse])
def list_carpoolings(event_id: int, skip: int = 0, limit: int = 100,
                     db: Session = Depends(get_db)):
    return CarpoolingService(db).list_by_event(event_id, skip, limit)


@router.get("/{carpooling_id}", response_model=CarpoolingResponse)
def get_carpooling(carpooling_id: int, db: Session = Depends(get_db)):
    c = CarpoolingService(db).get(carpooling_id)
    if not c:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")
    return c


@router.post("", response_model=CarpoolingResponse, status_code=status.HTTP_201_CREATED)
def create_carpooling(payload: CarpoolingCreate, db: Session = Depends(get_db),
                      current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("driver_id", None)
    return CarpoolingService(db).create(driver_id=current.id, **data)


@router.patch("/{carpooling_id}", response_model=CarpoolingResponse)
def update_carpooling(carpooling_id: int, payload: CarpoolingUpdate,
                      db: Session = Depends(get_db),
                      current: User = Depends(get_current_user)):
    service = CarpoolingService(db)
    c = service.get(carpooling_id)
    if not c:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")
    if c.driver_id != current.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    return service.update(carpooling_id, **payload.model_dump(exclude_unset=True))


@router.delete("/{carpooling_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_carpooling(carpooling_id: int, db: Session = Depends(get_db),
                      current: User = Depends(get_current_user)):
    service = CarpoolingService(db)
    c = service.get(carpooling_id)
    if not c:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")
    if c.driver_id != current.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    service.delete(carpooling_id)
