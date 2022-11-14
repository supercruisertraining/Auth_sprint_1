from urllib.parse import urljoin
from uuid import uuid4

import pytest
from aioredis import Redis
from aiohttp import ClientSession

from src.db.db import session_factory
from src.db.models import User
from tests.functional.test_data.user_test_data import test_create_users_list
from tests.functional.settings import test_config
from src.core.config import config


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


@pytest.mark.asyncio
async def test_update_user(login_test_users):
    update_dict = {"last_name": "Pupkin", "first_name": "Vasya", "role": "new_role"}
    users_login_data = login_test_users
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_UPDATE_USER)
    for user in users_login_data:
        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}",
                                          "X-Request_id": str(uuid4())}) as session:
            async with session.patch(url, json=update_dict) as response:
                status = response.status
                body = await response.json()
        with session_factory() as session:
            user_obj = session.query(User).get(user["user_id"])
            assert user_obj.first_name == update_dict["first_name"]
            assert user_obj.last_name == update_dict["last_name"]
            assert user_obj.role != update_dict["role"]

        # Возвращаем изменения назад
        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}",
                                          "X-Request_id": str(uuid4())}) as session:
            async with session.patch(url,
                                     json={"last_name": user["last_name"],
                                           "first_name": user["first_name"]}) as response:
                response.raise_for_status()
                body = await response.json()
        with session_factory() as session:
            user_obj = session.query(User).get(user["user_id"])
            assert user_obj.first_name == user["first_name"]
            assert user_obj.last_name == user["last_name"]

        # Удаляем созданные токены в redis
        redis = Redis(host=test_config.REDIS_HOST, port=test_config.REDIS_PORT, db=test_config.REDIS_DB_NUM)
        redis_bg = Redis(host=test_config.REDIS_BG_HOST, port=test_config.REDIS_BG_PORT, db=test_config.REDIS_BG_DB_NUM)
        bg_token_key = config.REDIS_BG_FORMAT_KEY.format(token=user["refresh_token"],
                                                         user_id=user["user_id"])
        await redis.delete(user["refresh_token"])
        await redis_bg.delete(bg_token_key)

        # Закрываем соединение с redis
        await redis.close()
        await redis_bg.close()
