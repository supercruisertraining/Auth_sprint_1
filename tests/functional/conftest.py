import asyncio
from urllib.parse import urljoin
from uuid import uuid4

import pytest
import pytest_asyncio
from aiohttp import ClientSession
from sqlalchemy import delete

from tests.functional.settings import test_config
from src.db.db import session_factory
from src.db.models import Role, User, UserAdmin
from utils.cli_admin import create_superuser
from tests.functional.test_data.user_test_data import test_create_users_list
from tests.functional.test_data.role_test_data import test_roles
from tests.functional.test_data.superuser_test_data import admin_user_1


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def create_role():
    try:
        with session_factory() as session:
            for test_role in test_roles:
                role = Role(role_name=test_role["role_name"],
                            position=test_role["position"],
                            description=test_role.get("description"))
                session.add(role)
            session.commit()
    except Exception:
        pass
    yield test_roles
    try:
        with session_factory() as session:
            stmt = delete(Role).where(Role.role_name.in_([role["role_name"] for role in test_roles]))
            session.execute(stmt)
            session.commit()
    except Exception:
        pass


@pytest_asyncio.fixture(scope="session")
async def create_test_users(create_role):
    new_test_users_data = []
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_CREATE_USER)
    async with ClientSession(headers={"X-Request_id": str(uuid4())}) as session:
        for user_data in test_create_users_list:
            async with session.post(url, json=user_data) as response:
                response.raise_for_status()
                body = await response.json()
                new_test_users_data.append({"user_id": body["user_id"],
                                            "username": user_data["username"],
                                            "password": user_data["password"],
                                            "last_name": user_data["last_name"],
                                            "first_name": user_data["first_name"]})
    yield new_test_users_data
    with session_factory() as session:
        stmt = delete(User).where(User.id.in_([user["user_id"] for user in new_test_users_data]))
        session.execute(stmt)
        session.commit()


@pytest_asyncio.fixture
async def login_test_users(create_test_users):
    test_users_data = create_test_users
    test_users_login_list = []
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_LOGIN_USER)
    async with ClientSession(headers={"X-Request_id": str(uuid4())}) as session:
        for user_data in test_users_data:
            async with session.post(url,
                                    json={
                                        "username": user_data["username"],
                                        "password": user_data["password"]
                                    }
                                    ) as response:
                body = await response.json()
                test_users_login_list.append({"user_id": user_data["user_id"],
                                              "username": user_data["username"],
                                              "password": user_data["password"],
                                              "access_token": body["access_token"],
                                              "refresh_token": body["refresh_token"],
                                              "last_name": user_data["last_name"],
                                              "first_name": user_data["first_name"]})
    return test_users_login_list


@pytest_asyncio.fixture(scope="session")
async def create_test_superuser(create_role):
    superuser_id = create_superuser(username=admin_user_1["username"], password=admin_user_1["password"])
    yield {"id": superuser_id, "username": admin_user_1["username"], "password": admin_user_1["password"]}

    # Удаляем админа
    with session_factory() as session:
        target_user = session.query(UserAdmin).get(superuser_id)
        session.delete(target_user)
        session.commit()


@pytest_asyncio.fixture
async def login_test_superuser(create_test_superuser):
    test_superuser_data = create_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_LOGIN)
    async with ClientSession(headers={"X-Request_id": str(uuid4())}) as session:
        async with session.post(url,
                                json={
                                    "username": test_superuser_data["username"],
                                    "password": test_superuser_data["password"]
                                }
                                ) as response:
            body = await response.json()
            return {"user_id": test_superuser_data["id"],
                    "username": test_superuser_data["username"],
                    "password": test_superuser_data["password"],
                    "access_token": body["access_token"],
                    "refresh_token": body["refresh_token"]}
