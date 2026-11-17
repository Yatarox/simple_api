from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.users import User
from src.services.base_service import BaseService
from src.core.security import hash_password


class UserService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def create(self, *, first_name, last_name, username, email, password, avatar_url=None) -> User:
        user = User(
            first_name=first_name, last_name=last_name,
            username=username, email=email.lower(),
            password_hash=hash_password(password),
            avatar_url=avatar_url,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Email ou username déjà utilisé")
        self.db.refresh(user)
        return user

    def update(self, id: int, **data) -> User | None:
        data.pop("email", None)
        data.pop("password", None)
        return super().update(id, **data)
