from sqlalchemy.orm import Session
from src.models.shopping import ShoppingItem
from src.services.base_service import BaseService
from src.services.event_service import EventService


class ShoppingService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, ShoppingItem)

    def list_by_event(self, event_id: int, skip=0, limit=100):
        return self.list(skip, limit, event_id=event_id)

    def check_shopping_enabled(self, event_id: int):
        event = EventService(self.db).get(event_id)
        if not event:
            raise ValueError("Event introuvable")
        return event.shopping_list_enabled

    def create(self, *, user_id: int, **data):
        if not self.check_shopping_enabled(data["event_id"]):
            raise PermissionError("La shopping list n'est pas activée pour cet événement")
        return super().create(user_id=user_id, **data)

    def update(self, id: int, **data):
        item = self.get(id)
        if item is None:
            return None
        if not self.check_shopping_enabled(item.event_id):
            raise PermissionError("La shopping list n'est pas activée pour cet événement")
        return super().update(id, **data)
