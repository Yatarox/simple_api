from sqlalchemy.orm import Session
from src.models.carpooling import Carpooling
from src.services.base_service import BaseService
from src.services.event_service import EventService


class CarpoolingService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Carpooling)

    def check_carpooling_enabled(self, event_id: int):
        event = EventService(self.db).get(event_id)
        if not event:
            raise ValueError("Event introuvable")
        return event.carpooling_enabled

    def create(self, *, driver_id: int, **data):
        if not self.check_carpooling_enabled(data["event_id"]):
            raise PermissionError("Le covoiturage n'est pas activé pour cet événement")
        event = EventService(self.db).get(data["event_id"])
        if data.get("departure_time") and data["departure_time"] >= event.start_time:
            raise ValueError("L'heure de départ doit être avant le début de l'événement")
        return super().create(driver_id=driver_id, **data)

    def update(self, id: int, **data):
        data.pop("driver_id", None)
        data.pop("event_id", None)
        item = self.get(id)
        if item is None:
            return None
        if not self.check_carpooling_enabled(item.event_id):
            raise PermissionError("Le covoiturage n'est pas activé pour cet événement")
        return super().update(id, **data)

    def list_by_event(self, event_id: int, skip=0, limit=100):
        return self.list(skip, limit, event_id=event_id)
