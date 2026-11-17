from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.ticket import TicketType, Ticket
from src.models.event import Event, EventOrganizer
from src.services.base_service import BaseService


class TicketTypeService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, TicketType)

    def create(self, *, user_id: int, **data):
        organizer = (
            self.db.query(EventOrganizer)
            .filter(EventOrganizer.event_id == data["event_id"],
                    EventOrganizer.user_id == user_id)
            .first()
        )
        if organizer is None:
            raise PermissionError("Seul un organisateur peut créer un type de billet")
        event = self.db.get(Event, data["event_id"])
        if not event.ticketing_enabled:
            raise PermissionError("La billetterie n'est pas activée pour cet événement")
        return super().create(**data)


class TicketService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Ticket)

    def create(self, *, event_id: int, ticket_type_id: int, **data) -> Ticket:
        event = self.db.get(Event, event_id)
        if event is None or event.visibility != "public" or not event.ticketing_enabled:
            raise ValueError("La billetterie n'est pas disponible pour cet événement")
        ttype = self.db.get(TicketType, ticket_type_id)
        if ttype is None or ttype.event_id != event_id:
            raise ValueError("Type de billet invalide")
        sold = self.db.query(Ticket).filter(Ticket.ticket_type_id == ticket_type_id).count()
        if sold >= ttype.quantity:
            raise ValueError("Plus de billets disponibles pour ce type")
        try:
            return super().create(event_id=event_id, ticket_type_id=ticket_type_id, **data)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Cette personne a déjà un billet pour cet événement")

    def check_ticketing_enabled(self, event_id: int):
        event = self.db.get(Event, event_id)
        if not event:
            raise ValueError("Event introuvable")
        if event.visibility != "public":
            return False
        return event.ticketing_enabled
