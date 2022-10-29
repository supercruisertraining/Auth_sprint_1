import pytest

from src.db.db import session_factory
from src.db.models import User
from tests.functional.test_data.user_test_data import test_create_users_list


@pytest.mark.parametrize("user_data", test_create_users_list)
@pytest.mark.asyncio
async def test_create_user(create_test_users, user_data):
    with session_factory() as session:
        user = session.query(User).filter(User.username == user_data["username"]).first()
    assert user
    if user_data.get("last_name"):
        assert user.last_name == user_data["last_name"]
    if user_data.get("first_name"):
        assert user.first_name == user_data["first_name"]
