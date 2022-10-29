from functools import lru_cache
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from services.db_service import get_db_service
from services.db_service import DBService
from schemas.user import UserModel, UserRegisterModel, UserUpdateModel


class UserService:

    def __init__(self, db_service: DBService):
        self.db_service = db_service

    def login_user(self, username: str, password: str) -> UserModel | None:
        exist_user = self.db_service.get_user_by_username(username)
        if exist_user:
            if self._check_password(password, exist_user.password):
                return exist_user
        return None

    def validate_to_create(self, user: UserRegisterModel | UserUpdateModel):
        exist_user = self.db_service.get_user_by_username(user.username)
        if exist_user:
            return False, "Such username already exists"
        return True, ""

    def create_user(self, user: UserRegisterModel) -> str:
        new_id = self.db_service.create_user(username=user.username, password=self._cook_password_to_db(user.password),
                                             first_name=user.first_name, last_name=user.last_name)
        if new_id:
            new_id = str(new_id)
        return new_id

    def update_user(self, user_id: str, user: UserUpdateModel):
        if user.password:
            user.password = self._cook_password_to_db(user.password)
        self.db_service.update_user(user_id=user_id, **user.dict())

    def add_login_record(self, user_id: str, user_ip: str | None = None, user_os: str | None = None,
                         user_browser: str | None = None, user_device: str | None = None):
        self.db_service.add_login_record(user_id=user_id, user_ip=user_ip, user_os=user_os, user_browser=user_browser,
                                         user_device=user_device, datetime_utc=datetime.utcnow().isoformat(sep=" "))

    def get_user_by_user_id(self, user_id: str):
        return self.db_service.get_user_by_id(user_id)

    def get_login_stat_list(self, user_id: str) -> list[dict]:
        return list(map(lambda x: {"ip": x.ip, "os": x.os, "device": x.device, "browser": x.browser,
                                   "datetime_utc": x.created_at_utc}, self.db_service.get_login_stat(user_id)))

    def assign_role(self, user_id: str, role: str):
        if not self.db_service.get_role(role):
            raise Exception("No such role")
        self.db_service.update_role(user_id, role)

    def _check_password(self, provided_password, user_password):
        return check_password_hash(user_password, provided_password)

    def _cook_password_to_db(self, password: str):
        return generate_password_hash(password)


@lru_cache
def get_user_service():
    return UserService(get_db_service())
