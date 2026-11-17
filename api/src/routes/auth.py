from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import create_access_token, verify_password
from src.schemas.auth import RegisterRequest, TokenResponse
from src.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte utilisateur",
    description="Crée un nouveau compte avec un nom, un email et un mot de passe.",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = UserService(db).create(
            first_name=payload.first_name,
            last_name=payload.last_name,
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Se connecter",
    description=(
        "Vérifie les identifiants de l'utilisateur et retourne "
        "un token JWT pour accéder aux routes protégées."
    ),
)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = UserService(db).get_by_email(form.username.lower())

    if user is None or not verify_password(
        form.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
    )