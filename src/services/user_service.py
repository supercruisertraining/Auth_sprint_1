from schemas.user import UserModel
from functools import lru_cache
from services.db_service import get_db_service
from lib.errors import ValidationError
from services.db_service import DBService


class UserService:

    def __init__(self, db_service: DBService):
        self.db_service = db_service

    def register_user(self, user_data: UserModel) -> None:
        pass

    def validate_to_create(self, user: UserModel):
        exist_user = self.db_service.get_user_by_username(user.username)
        if exist_user:
            raise ValidationError("This username already exists")

    def create_user(self, user: UserModel):
        self.db_service.create_user(username=user.username, password=user.password,
                                    first_name=user.first_name, last_name=user.last_name)


@lru_cache
def get_user_service():
    return UserService(get_db_service())
