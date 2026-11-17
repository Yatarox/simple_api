from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import create_access_token, verify_password
from src.schemas.auth import RegisterRequest, TokenResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        user = service.create(
            first_name=payload.first_name,
            last_name=payload.last_name,
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"id": user.id, "email": user.email, "username": user.username}


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_by_email(form.username.lower())
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    return TokenResponse(access_token=create_access_token(user.id))
