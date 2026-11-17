from sqlalchemy.orm import Session
from src.models.poll import Poll, PollQuestion, PollOption, PollAnswer
from src.models.event import EventOrganizer, EventParticipant
from src.services.base_service import BaseService


class PollService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Poll)

    def create(self, *, created_by: int, **data):
        organizer = (
            self.db.query(EventOrganizer)
            .filter(EventOrganizer.event_id == data["event_id"],
                    EventOrganizer.user_id == created_by)
            .first()
        )
        if organizer is None:
            raise PermissionError("Seul un organisateur peut créer un sondage")
        return super().create(created_by=created_by, **data)


class PollQuestionService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, PollQuestion)


class PollOptionService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, PollOption)


class PollAnswerService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, PollAnswer)

    def create(self, *, question_id: int, option_id: int, user_id: int) -> PollAnswer:
        opt = self.db.get(PollOption, option_id)
        if opt is None or opt.question_id != question_id:
            raise ValueError("L'option ne correspond pas à la question")
        question = self.db.get(PollQuestion, question_id)
        poll = self.db.get(Poll, question.poll_id)
        participant = (
            self.db.query(EventParticipant)
            .filter(EventParticipant.event_id == poll.event_id,
                    EventParticipant.user_id == user_id)
            .first()
        )
        if participant is None:
            raise PermissionError("Seul un participant peut répondre au sondage")
        return super().create(question_id=question_id, option_id=option_id, user_id=user_id)
