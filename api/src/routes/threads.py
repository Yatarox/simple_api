from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.thread import ThreadCreate, ThreadResponse, ThreadMessageCreate, MessageResponse
from src.services.thread_service import ThreadService

router = APIRouter(prefix="/threads", tags=["threads"])


@router.post("", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
def create_thread(payload: ThreadCreate, db: Session = Depends(get_db),
                  current: User = Depends(get_current_user)):
    try:
        return ThreadService(db).create(group_id=payload.group_id, event_id=payload.event_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{thread_id}", response_model=ThreadResponse)
def get_thread(thread_id: int, db: Session = Depends(get_db)):
    t = ThreadService(db).get(thread_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread introuvable")
    return t


@router.get("/{thread_id}/messages", response_model=list[MessageResponse])
def list_messages(thread_id: int, skip: int = 0, limit: int = 100,
                  db: Session = Depends(get_db)):
    return ThreadService(db).get_messages(thread_id, skip, limit)


@router.post("/{thread_id}/messages", response_model=MessageResponse,
             status_code=status.HTTP_201_CREATED)
def post_message(thread_id: int, payload: ThreadMessageCreate,
                 db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    service = ThreadService(db)
    if not service.get(thread_id):
        raise HTTPException(status_code=404, detail="Thread introuvable")
    data = payload.model_dump()
    data.pop("thread_id", None)
    data.pop("user_id", None)              # 🔒 forcé par le token
    return service.add_message(thread_id=thread_id, user_id=current.id, **data)
