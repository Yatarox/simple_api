from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.group import Group, GroupMember
from src.services.base_service import BaseService


class GroupService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Group)

    def create(self, *, creator_id: int, **data) -> Group:
        group = Group(**data)
        self.db.add(group)
        self.db.flush()                       # récupère group.id sans commit
        self.db.add(GroupMember(group_id=group.id, user_id=creator_id, role="admin"))
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Groupe invalide")
        self.db.refresh(group)
        return group

    def get_members(self, group_id: int) -> list[GroupMember]:
        return self.db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

    def add_member(self, group_id: int, user_id: int, role: str = "member") -> GroupMember:
        m = GroupMember(group_id=group_id, user_id=user_id, role=role)
        self.db.add(m)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Membre déjà présent dans le groupe")
        self.db.refresh(m)
        return m
