from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users import User
from src.schemas.photo import (PhotoAlbumCreate, PhotoAlbumResponse,
                               PhotoCreate, PhotoUpdate, PhotoResponse,
                               PhotoCommentCreate, PhotoCommentResponse)
from src.services.photo_service import PhotoAlbumService, PhotoService, PhotoCommentService

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/albums", response_model=PhotoAlbumResponse, status_code=status.HTTP_201_CREATED)
def create_album(payload: PhotoAlbumCreate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    return PhotoAlbumService(db).create(**payload.model_dump())


@router.get("/albums/{album_id}", response_model=PhotoAlbumResponse)
def get_album(album_id: int, db: Session = Depends(get_db)):
    a = PhotoAlbumService(db).get(album_id)
    if not a:
        raise HTTPException(status_code=404, detail="Album introuvable")
    return a


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def create_photo(payload: PhotoCreate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("user_id", None)
    return PhotoService(db).create(user_id=current.id, **data)


@router.patch("/{photo_id}", response_model=PhotoResponse)
def update_photo(photo_id: int, payload: PhotoUpdate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    service = PhotoService(db)
    p = service.get(photo_id)
    if not p:
        raise HTTPException(status_code=404, detail="Photo introuvable")
    if p.user_id != current.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    return service.update(photo_id, **payload.model_dump(exclude_unset=True))


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(photo_id: int, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    service = PhotoService(db)
    p = service.get(photo_id)
    if not p:
        raise HTTPException(status_code=404, detail="Photo introuvable")
    if p.user_id != current.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    service.delete(photo_id)


@router.post("/{photo_id}/comments", response_model=PhotoCommentResponse,
             status_code=status.HTTP_201_CREATED)
def comment_photo(photo_id: int, payload: PhotoCommentCreate,
                  db: Session = Depends(get_db),
                  current: User = Depends(get_current_user)):
    data = payload.model_dump()
    data.pop("photo_id", None)
    data.pop("user_id", None)
    return PhotoCommentService(db).create(photo_id=photo_id, user_id=current.id, **data)
