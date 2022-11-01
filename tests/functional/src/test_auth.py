import json
from urllib.parse import urljoin
from asyncio import sleep
from random import randint

import pytest
from aioredis import Redis
from aiohttp import ClientSession

from src.db.db import session_factory
from src.db.models import User
from tests.functional.test_data.user_test_data import test_create_users_list
from tests.functional.test_data.role_test_data import test_role_names
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
async def test_login_user(login_test_users):
    users_login_data = login_test_users
    redis = Redis(host=test_config.REDIS_HOST, port=test_config.REDIS_PORT, db=test_config.REDIS_DB_NUM)
    redis_bg = Redis(host=test_config.REDIS_BG_HOST, port=test_config.REDIS_BG_PORT, db=test_config.REDIS_BG_DB_NUM)
    for login_data in users_login_data:
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

        await redis.delete(login_data["refresh_token"])
        await redis_bg.delete(bg_token_key)

        # Закрываем соединение с redis
        await redis.close()
        await redis_bg.close()


@pytest.mark.asyncio
async def test_update_user(login_test_users):
    update_dict = {"last_name": "Pupkin", "first_name": "Vasya", "role": "new_role"}
    users_login_data = login_test_users
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_UPDATE_USER)
    for user in users_login_data:
        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}"}) as session:
            async with session.patch(url, json=update_dict) as response:
                status = response.status
                body = await response.json()
        with session_factory() as session:
            user_obj = session.query(User).get(user["user_id"])
            assert user_obj.first_name == update_dict["first_name"]
            assert user_obj.last_name == update_dict["last_name"]
            assert user_obj.role != update_dict["role"]

        # Возвращаем изменения назад
        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}"}) as session:
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


@pytest.mark.asyncio
async def test_soft_logout(login_test_users):
    users_login_data = login_test_users
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_SOFT_LOGOUT_USER)
    redis = Redis(host=test_config.REDIS_HOST, port=test_config.REDIS_PORT, db=test_config.REDIS_DB_NUM)
    for user in users_login_data:
        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}"}) as session:
            async with session.delete(url, json={"refresh_token": user["refresh_token"]}) as response:
                assert response.ok
        result = await redis.delete(user["refresh_token"])
        assert not result
    # Закрываем соединение с redis
    await redis.close()


@pytest.mark.asyncio
async def test_hard_logout(login_test_users):
    users_login_data = login_test_users
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_HARD_LOGOUT_USER)
    url_login = urljoin(test_config.API_BASE_URL, test_config.API_PATH_LOGIN_USER)
    redis = Redis(host=test_config.REDIS_HOST, port=test_config.REDIS_PORT, db=test_config.REDIS_DB_NUM)
    for user in users_login_data:
        await sleep(1)
        async with ClientSession() as session:
            # Эмулируем вход еще с одного, или нескольких устройств
            for _ in range(randint(1, 5)):
                async with session.post(url_login,
                                        json={"username": user["username"], "password": user["password"]}) as response:
                    response.raise_for_status()

        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}"}) as session:
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

    # Закрываем соединение с redis
    await redis.close()


@pytest.mark.asyncio
async def test_refresh(login_test_users):
    users_login_data = login_test_users
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_REFRESH)
    redis = Redis(host=test_config.REDIS_HOST, port=test_config.REDIS_PORT, db=test_config.REDIS_DB_NUM)
    await sleep(1)
    for user in users_login_data:
        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}"}) as session:
            async with session.put(url, json={"refresh_token": user["refresh_token"]}) as response:
                response.raise_for_status()
                body = await response.json()
        assert user["refresh_token"] != body["refresh_token"]
        assert user["access_token"] != body["access_token"]
        assert await redis.delete(body["refresh_token"])
        assert not await redis.delete(body["refresh_token"])
    await redis.close()


@pytest.mark.asyncio
async def test_assign_role(login_test_users):
    users_login_data = login_test_users
    url = urljoin(test_config.API_BASE_URL, test_config.API_ASSIGN_USER_ROLE)
    not_existing_role_name = "not_existing_role"
    for user in users_login_data:
        async with ClientSession(headers={"Authorization": f"Bearer {user['access_token']}"}) as session:

            # Проверяем негативный случай: попытка присвоения несуществующей роли
            async with session.patch(url, json={"role": not_existing_role_name}) as response:
                assert not response.ok
            with session_factory() as db_session:
                user_obj = db_session.query(User).get(user["user_id"])
                assert user_obj.role != not_existing_role_name

            async with session.patch(url, json={"role": test_role_names[0]}) as response:
                assert response.ok
            with session_factory() as db_session:
                user_obj = db_session.query(User).get(user["user_id"])
                assert user_obj.role == test_role_names[0]