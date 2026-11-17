# app/services/base_service.py
from sqlalchemy.orm import Session


class BaseService:
    """CRUD générique. Les services métier héritent et surchargent au besoin."""

    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    def get(self, id: int):
        return self.db.get(self.model, id)

    def list(self, skip: int = 0, limit: int = 100, **filters) -> list:
        q = self.db.query(self.model)
        for field, value in filters.items():
            q = q.filter(getattr(self.model, field) == value)
        return q.offset(skip).limit(limit).all()

    def create(self, **data):
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, **data):
        obj = self.get(id)
        if obj is None:
            return None
        for k, v in data.items():
            if v is not None:            # PATCH : on ne touche pas aux champs non fournis
                setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
