from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse
from src.services.shopping_service import ShoppingService

router = APIRouter(prefix="/shopping", tags=["shopping"])


@router.get("", response_model=list[ShoppingItemResponse])
def list_items(event_id: int, skip: int = 0, limit: int = 100,
               db: Session = Depends(get_db)):
    return ShoppingService(db).list_by_event(event_id, skip, limit)


@router.post("", response_model=ShoppingItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(payload: ShoppingItemCreate, db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("user_id", None)
    return ShoppingService(db).create(user_id=current.id, **data)


@router.patch("/{item_id}", response_model=ShoppingItemResponse)
def update_item(item_id: int, payload: ShoppingItemUpdate, db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    service = ShoppingService(db)
    item = service.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item introuvable")
    if item.user_id != current.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    return service.update(item_id, **payload.model_dump(exclude_unset=True))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    service = ShoppingService(db)
    item = service.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item introuvable")
    if item.user_id != current.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    service.delete(item_id)
