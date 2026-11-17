from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.poll import (
    PollAnswerCreate,
    PollAnswerResponse,
    PollCreate,
    PollOptionCreate,
    PollOptionResponse,
    PollQuestionCreate,
    PollQuestionResponse,
    PollResponse,
)
from src.services.poll_service import (
    PollAnswerService,
    PollOptionService,
    PollQuestionService,
    PollService,
)


router = APIRouter(
    prefix="/polls",
    tags=["Sondages"],
)


@router.post(
    "",
    response_model=PollResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un sondage",
    description=(
        "Crée un sondage pour un événement. "
        "Seul un organisateur de l'événement peut le créer."
    ),
)
def create_poll(
    payload: PollCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    data = payload.model_dump()
    data.pop("created_by", None)

    try:
        return PollService(db).create(
            created_by=current.id,
            **data,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get(
    "/{poll_id}",
    response_model=PollResponse,
    summary="Obtenir un sondage",
    description="Retourne les informations d'un sondage grâce à son identifiant.",
)
def get_poll(
    poll_id: int,
    db: Session = Depends(get_db),
):
    poll = PollService(db).get(poll_id)

    if poll is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sondage introuvable",
        )

    return poll


@router.post(
    "/{poll_id}/questions",
    response_model=PollQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une question",
    description="Ajoute une question à un sondage existant.",
)
def add_question(
    poll_id: int,
    payload: PollQuestionCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return PollQuestionService(db).create(
        poll_id=poll_id,
        question=payload.question,
    )


@router.post(
    "/questions/{question_id}/options",
    response_model=PollOptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une option",
    description="Ajoute une réponse possible à une question de sondage.",
)
def add_option(
    question_id: int,
    payload: PollOptionCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return PollOptionService(db).create(
        question_id=question_id,
        option_text=payload.option_text,
    )


@router.post(
    "/answers",
    response_model=PollAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Répondre à un sondage",
    description=(
        "Enregistre la réponse d'un utilisateur à une question. "
        "Un participant ne peut répondre qu'une seule fois par question."
    ),
)
def answer_poll(
    payload: PollAnswerCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        return PollAnswerService(db).create(
            question_id=payload.question_id,
            option_id=payload.option_id,
            user_id=current.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )