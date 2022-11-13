from functools import lru_cache
from uuid import UUID

from sqlalchemy import desc

from db.db import session_factory
from db.models import User, UserAdmin, LoginStat, Role, Password
from schemas.user import UserModel, UserAdminModel
from schemas.role import Role as RoleSchema


class DBService:
    def __init__(self, db_session):
        self.db = db_session

    def get_user_by_username(self, username: str) -> UserModel | None:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        pswd_data = self.db.query(Password).filter(Password.user_id == user.id).first()
        if pswd_data:
            password = pswd_data.password
        else:
            password = None
        user_model = UserModel(id=user.id, username=user.username, password=password, email=user.email,
                               role=user.role, first_name=user.first_name, last_name=user.last_name)
        user_model.id = str(user_model.id)
        return user_model

    def get_superuser_by_username(self, username: str) -> UserModel | None:
        user = self.db.query(UserAdmin).filter(UserAdmin.username == username).first()
        if not user:
            return None
        user_model = UserModel.from_orm(user)
        user_model.id = str(user_model.id)
        return user_model

    def get_user_by_id(self, user_id: str) -> UserModel | None:
        user = self.db.query(User).get(user_id)
        if not user:
            return None
        pswd_data = self.db.query(Password).filter(Password.user_id == user.id).first()
        if pswd_data:
            password = pswd_data.password
        else:
            password = None
        user_model = UserModel(id=user.id, username=user.username, password=password, email=user.email,
                               role=user.role, first_name=user.first_name, last_name=user.last_name)
        user_model.id = str(user_model.id)
        return user_model

    def get_superuser_by_id(self, user_id: str) -> UserModel | None:
        user = self.db.query(UserAdmin).get(user_id)
        if not user:
            return None
        user_model = UserModel.from_orm(user)
        user_model.id = str(user_model.id)
        return user_model

    def create_user(self, username: str, password: str, email: str | None,
                    last_name: str | None = None, first_name: str | None = None) -> UUID:
        new_user = User(username=username,
                        email=email,
                        last_name=last_name,
                        first_name=first_name)
        self.db.add(new_user)
        self.db.flush()
        new_password = Password(user_id=new_user.id, password=password)
        self.db.add(new_password)
        self.db.commit()
        return new_user.id

    def create_superuser(self, username: str, password: str,
                         last_name: str | None = None, first_name: str | None = None) -> UUID:
        new_user = UserAdmin(username=username,
                             password=password,
                             last_name=last_name,
                             first_name=first_name)
        self.db.add(new_user)
        self.db.commit()
        return new_user.id

    def get_superusers_from_db(self) -> list[UserAdminModel]:
        super_users_orm = self.db.query(UserAdmin).all()
        return list(map(UserAdminModel.from_orm, super_users_orm))

    def update_user(self, user_id: str, username: str | None = None, password: str | None = None,
                    last_name: str | None = None, first_name: str | None = None):
        update_dict = {"username": username,
                       "last_name": last_name,
                       "first_name": first_name}
        user_obj = self.db.query(User).get(user_id)
        for key, value in {key: value for key, value in update_dict.items() if value}.items():
            setattr(user_obj, key, value)
        if password:
            pswd = self.db.query(Password).filter(Password.user_id == user_id).first()
            pswd.update({"password": password})
        self.db.commit()

    def add_login_record(self, user_id: str, user_ip: str | None, user_os: str | None, user_browser: str | None,
                         user_device: str | None, datetime_utc: str):
        self.db.add(LoginStat(user_id=user_id, ip=user_ip, os=user_os, browser=user_browser,
                              device=user_device, created_at_utc=datetime_utc))
        self.db.commit()

    def get_login_stat(self, user_id: str, limit: int, offset: int) -> list[LoginStat]:
        return self.db.query(LoginStat).filter(LoginStat.user_id == user_id)\
            .order_by(desc(LoginStat.created_at_utc)).limit(limit).offset(offset).all()

    def get_role(self, role_name: str) -> Role:
        return self.db.query(Role).get(role_name)

    def get_roles_list(self) -> list[RoleSchema]:
        return list(map(RoleSchema.from_orm, self.db.query(Role).all()))

    def update_user_role(self, user_id: str, role: str):
        user_obj = self.db.query(User).get(user_id)
        user_obj.role = role
        self.db.commit()

    def admin_create_role(self, role_name: str, position: int, description: str | None = None):
        self.db.add(Role(role_name=role_name, position=position, description=description))
        self.db.commit()

    def admin_delete_role(self, role_name):
        target_role = self.db.query(Role).get(role_name)
        self.db.delete(target_role)
        self.db.commit()

    def admin_update_role(self, role_name: str, position: int | None = None, description: str | None = None):
        if position or description:
            role = self.db.query(Role).get(role_name)
            if description:
                role.description = description
            if position:
                role.position = position
            self.db.commit()


@lru_cache
def get_db_service():
    return DBService(session_factory())
