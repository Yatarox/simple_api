from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.poll import (PollCreate, PollResponse,
                              PollQuestionCreate, PollQuestionResponse,
                              PollOptionCreate, PollOptionResponse,
                              PollAnswerCreate, PollAnswerResponse)
from src.services.poll_service import (PollService, PollQuestionService,
                                       PollOptionService, PollAnswerService)

router = APIRouter(prefix="/polls", tags=["polls"])


@router.post("", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
def create_poll(payload: PollCreate, db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("created_by", None)
    return PollService(db).create(created_by=current.id, **data)


@router.get("/{poll_id}", response_model=PollResponse)
def get_poll(poll_id: int, db: Session = Depends(get_db)):
    p = PollService(db).get(poll_id)
    if not p:
        raise HTTPException(status_code=404, detail="Sondage introuvable")
    return p


@router.post("/{poll_id}/questions", response_model=PollQuestionResponse,
             status_code=status.HTTP_201_CREATED)
def add_question(poll_id: int, payload: PollQuestionCreate,
                 db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("poll_id", None)
    return PollQuestionService(db).create(poll_id=poll_id, **data)


@router.post("/questions/{question_id}/options", response_model=PollOptionResponse,
             status_code=status.HTTP_201_CREATED)
def add_option(question_id: int, payload: PollOptionCreate,
               db: Session = Depends(get_db),
               current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("question_id", None)
    return PollOptionService(db).create(question_id=question_id, **data)


@router.post("/answers", response_model=PollAnswerResponse,
             status_code=status.HTTP_201_CREATED)
def answer(payload: PollAnswerCreate, db: Session = Depends(get_db),
           current: User = Depends(get_current_user)):
    return PollAnswerService(db).create(
        question_id=payload.question_id,
        option_id=payload.option_id,
        user_id=current.id,
    )
