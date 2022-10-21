from functools import lru_cache

from db.db import session_factory
from db.models import User


class DBService:
    def __init__(self, db_session):
        self.db = db_session

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, password: str, last_name: str | None = None, first_name: str | None = None):
        self.db.add(User(username=username, password=password, last_name=last_name, first_name=first_name))
        self.db.commit()

    def _cook_password_to_db(self, password: str):
        return password


@lru_cache
def get_db_service():
    return DBService(session_factory())
