from functools import lru_cache
from services.db_service import get_db_service
from services.db_service import DBService
from schemas.user import UserModel


class UserService:

    def __init__(self, db_service: DBService):
        self.db_service = db_service

    def login_user(self, username: str, password: str) -> UserModel | None:
        exist_user = self.db_service.get_user_by_username(username)
        if exist_user:
            converted_provided_password = self.db_service.cook_password_to_db(password)
            if converted_provided_password == password:
                return exist_user
        return None

    def validate_to_create(self, user: UserModel):
        exist_user = self.db_service.get_user_by_username(user.username)
        if exist_user:
            return False, "Such username already exists"
        return True, ""

    def create_user(self, user: UserModel):
        self.db_service.create_user(username=user.username, password=user.password,
                                    first_name=user.first_name, last_name=user.last_name)

    def get_user_by_user_id(self, user_id: str):
        return self.db_service.get_user_by_id(user_id)


@lru_cache
def get_user_service():
    return UserService(get_db_service())
