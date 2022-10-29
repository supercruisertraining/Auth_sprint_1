from functools import lru_cache
from uuid import UUID

from sqlalchemy import desc

from db.db import session_factory
from db.models import User, LoginStat, Role
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

    def create_user(self, username: str, password: str,
                    last_name: str | None = None, first_name: str | None = None) -> UUID:
        new_user = User(username=username,
                        password=password,
                        last_name=last_name,
                        first_name=first_name)
        self.db.add(new_user)
        self.db.commit()
        return new_user.id

    def update_user(self, user_id: str, username: str | None = None, password: str | None = None,
                    last_name: str | None = None, first_name: str | None = None):
        update_dict = {"username": username,
                       "password": password,
                       "last_name": last_name,
                       "first_name": first_name}
        user_obj = self.db.query(User).get(user_id)
        for key, value in {key: value for key, value in update_dict.items() if value}.items():
            setattr(user_obj, key, value)
        self.db.commit()

    def add_login_record(self, user_id: str, user_ip: str | None, user_os: str | None, user_browser: str | None,
                         user_device: str | None, datetime_utc: str):
        self.db.add(LoginStat(user_id=user_id, ip=user_ip, os=user_os, browser=user_browser,
                              device=user_device, created_at_utc=datetime_utc))
        self.db.commit()

    def get_login_stat(self, user_id: str) -> list[LoginStat]:
        return self.db.query(LoginStat).filter(LoginStat.user_id == user_id)\
            .order_by(desc(LoginStat.created_at_utc)).all()

    def get_role(self, role_name: str):
        return self.db.query(Role).get(role_name)

    def update_role(self, user_id: str, role: str):
        user_obj = self.db.query(User).get(user_id)
        user_obj.role = role
        self.db.commit()


@lru_cache
def get_db_service():
    return DBService(session_factory())
