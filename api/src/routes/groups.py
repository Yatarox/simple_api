from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.permissions import is_group_admin
from src.models.users import User
from src.schemas.group import (GroupCreate, GroupUpdate, GroupResponse,
                               GroupMemberCreate, GroupMemberResponse)
from src.services.group_service import GroupService

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=list[GroupResponse])
def list_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return GroupService(db).list(skip, limit)


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    g = GroupService(db).get(group_id)
    if not g:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    return g


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    return GroupService(db).create(creator_id=current.id, **payload.model_dump())


@router.patch("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, payload: GroupUpdate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    if not is_group_admin(db, current.id, group_id):
        raise HTTPException(status_code=403, detail="Non autorisé")
    g = GroupService(db).update(group_id, **payload.model_dump(exclude_unset=True))
    if not g:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    return g


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    if not is_group_admin(db, current.id, group_id):
        raise HTTPException(status_code=403, detail="Non autorisé")
    if not GroupService(db).delete(group_id):
        raise HTTPException(status_code=404, detail="Groupe introuvable")


@router.get("/{group_id}/members", response_model=list[GroupMemberResponse])
def list_members(group_id: int, db: Session = Depends(get_db)):
    return GroupService(db).get_members(group_id)


@router.post("/{group_id}/members", response_model=GroupMemberResponse,
             status_code=status.HTTP_201_CREATED)
def add_member(group_id: int, payload: GroupMemberCreate, db: Session = Depends(get_db),
               current: User = Depends(get_current_user)):
    if not is_group_admin(db, current.id, group_id):
        raise HTTPException(status_code=403, detail="Non autorisé")
    return GroupService(db).add_member(group_id, payload.user_id, payload.role)
