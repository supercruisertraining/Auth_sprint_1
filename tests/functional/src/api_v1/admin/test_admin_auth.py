import json
import jwt
from urllib.parse import urljoin
from asyncio import sleep
from random import randint
from uuid import uuid4

import pytest
from aioredis import Redis
from aiohttp import ClientSession

from tests.functional.settings import test_config
from src.core.config import config
from src.db.db import session_factory
from src.db.models import UserAdmin


@pytest.mark.asyncio
async def test_create_superuser(create_test_superuser):
    superuser_data = create_test_superuser
    with session_factory() as db_session:
        user = db_session.query(UserAdmin).get(superuser_data["id"])
    assert user
    assert user.username == superuser_data["username"]


@pytest.mark.asyncio
async def test_login_superuser(login_test_superuser):
    login_data = login_test_superuser
    redis = Redis(host=test_config.REDIS_ADMIN_HOST,
                  port=test_config.REDIS_ADMIN_PORT,
                  db=test_config.REDIS_ADMIN_DB_NUM)
    redis_bg = Redis(host=test_config.REDIS_ADMIN_BG_HOST,
                     port=test_config.REDIS_ADMIN_BG_PORT,
                     db=test_config.REDIS_ADMIN_BG_DB_NUM)
    result_raw = await redis.get(login_data["refresh_token"])
    assert result_raw
    result_dict = json.loads(result_raw)
    assert result_dict["user_id"] == login_data["user_id"]
    bg_token_key = config.REDIS_BG_FORMAT_KEY.format(token=login_data["refresh_token"],
                                                     user_id=login_data["user_id"])
    result_raw = await redis_bg.get(bg_token_key)
    assert result_raw
    result_dict = json.loads(result_raw)
    assert result_dict["user_id"] == login_data["user_id"]

    assert jwt.decode(login_data["access_token"],
                      config.JWT_SECRET,
                      algorithms=[config.JWT_ALGORITHM]).get("is_admin", False)

    await redis.delete(login_data["refresh_token"])
    await redis_bg.delete(bg_token_key)

    # Закрываем соединение с redis
    await redis.close()
    await redis_bg.close()


@pytest.mark.asyncio
async def test_logout_superuser(login_test_superuser):
    user = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_LOGOUT)
    url_login = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_LOGIN)
    redis = Redis(host=test_config.REDIS_ADMIN_HOST,
                  port=test_config.REDIS_ADMIN_PORT,
                  db=test_config.REDIS_ADMIN_DB_NUM)
    await sleep(1)
    async with ClientSession(headers={"X-Request_id": str(uuid4())}) as session:
        # Эмулируем вход еще с одного или нескольких устройств
        for _ in range(randint(1, 5)):
            async with session.post(url_login,
                                    json={"username": user["username"], "password": user["password"]}) as response:
                response.raise_for_status()

    async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}",
                                      "X-Request_id": str(uuid4())}) as session:
        async with session.delete(url, json={"refresh_token": user["refresh_token"]}) as response:
            assert response.ok
    result = await redis.delete(user["refresh_token"])
    assert not result
    has_users_keys = False
    keys_list = await redis.keys(pattern="*")
    for key in keys_list:
        data_raw = await redis.get(key)
        data = json.loads(data_raw)
        if data.get("user_id") == user["user_id"]:
            has_users_keys = True
            await redis.delete(key)
    assert not has_users_keys


@pytest.mark.asyncio
async def test_admin_refresh(login_test_superuser):
    user = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_ADMIN_REFRESH)
    redis = Redis(host=test_config.REDIS_ADMIN_HOST,
                  port=test_config.REDIS_ADMIN_PORT,
                  db=test_config.REDIS_ADMIN_DB_NUM)
    await sleep(1)
    async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}",
                                      "X-Request_id": str(uuid4())}) as session:
        async with session.put(url, json={"refresh_token": user["refresh_token"]}) as response:
            response.raise_for_status()
            body = await response.json()
    assert user["refresh_token"] != body["refresh_token"]
    assert user["access_token"] != body["access_token"]
    assert await redis.delete(body["refresh_token"])
    assert not await redis.delete(user["refresh_token"])
    await redis.close()
