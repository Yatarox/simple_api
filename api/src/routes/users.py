from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.user import UserResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def me(current: User = Depends(get_current_user)):
    return current


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService(db).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(payload: UserUpdate, db: Session = Depends(get_db),
              current: User = Depends(get_current_user)):
    try:
        user = UserService(db).update(current.id, **payload.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    UserService(db).delete(current.id)
