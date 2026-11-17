from sqlalchemy.orm import Session
from src.models.photo import PhotoAlbum, Photo, PhotoComment
from src.models.event import EventParticipant
from src.services.base_service import BaseService


class PhotoAlbumService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, PhotoAlbum)


class PhotoService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Photo)

    def create(self, *, user_id: int, **data):
        album = self.db.get(PhotoAlbum, data["album_id"])
        if album is None:
            raise ValueError("Album introuvable")
        participant = (
            self.db.query(EventParticipant)
            .filter(EventParticipant.event_id == album.event_id,
                    EventParticipant.user_id == user_id)
            .first()
        )
        if participant is None:
            raise PermissionError("Seul un participant peut poster une photo")
        return super().create(user_id=user_id, **data)

    def update(self, id: int, **data):
        data.pop("user_id", None)
        data.pop("album_id", None)
        return super().update(id, **data)


class PhotoCommentService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, PhotoComment)

    def create(self, *, user_id: int, **data):
        photo = self.db.get(Photo, data["photo_id"])
        if photo is None:
            raise ValueError("Photo introuvable")
        album = self.db.get(PhotoAlbum, photo.album_id)
        participant = (
            self.db.query(EventParticipant)
            .filter(EventParticipant.event_id == album.event_id,
                    EventParticipant.user_id == user_id)
            .first()
        )
        if participant is None:
            raise PermissionError("Seul un participant peut commenter la photo")
        return super().create(user_id=user_id, **data)
