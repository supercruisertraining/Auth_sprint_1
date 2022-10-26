from functools import lru_cache

from db.db import session_factory
from db.models import User
from schemas.user import UserModel


class DBService:
    def __init__(self, db_session):
        self.db = db_session

    def get_user_by_username(self, username: str) -> UserModel | None:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        user_model = UserModel.from_orm(user)
        user_model.id = str(user_model.id)
        return user_model

    def get_user_by_id(self, user_id: str) -> UserModel | None:
        user = self.db.query(User).get(user_id)
        if not user:
            return None
        user_model = UserModel.from_orm(user)
        user_model.id = str(user_model.id)
        return user_model

    def create_user(self, username: str, password: str, last_name: str | None = None, first_name: str | None = None):
        self.db.add(User(username=username,
                         password=self.cook_password_to_db(password),
                         last_name=last_name,
                         first_name=first_name))
        self.db.commit()

    def cook_password_to_db(self, password: str):
        return password


@lru_cache
def get_db_service():
    return DBService(session_factory())
