import asyncio
from urllib.parse import urljoin

import pytest
import pytest_asyncio
from aiohttp import ClientSession
from sqlalchemy import delete

from tests.functional.settings import test_config
from src.db.db import session_factory
from src.db.models import Role, User
from tests.functional.test_data.user_test_data import test_create_users_list
from tests.functional.test_data.role_test_data import test_role_names


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
            for role_name in test_role_names:
                role = Role(role_name=role_name)
                session.add(role)
            session.commit()
    except Exception:
        pass
    yield
    try:
        with session_factory() as session:
            stmt = delete(Role).where(Role.role_name.in_(test_role_names))
            session.execute(stmt)
            session.commit()
    except Exception:
        pass


@pytest_asyncio.fixture(scope="session")
async def create_test_users(create_role):
    new_test_users_ids = []
    url = urljoin(test_config.API_BASE_URL, test_config.API_PATH_CRETE_USER)
    async with ClientSession() as session:
        for user_data in test_create_users_list:
            async with session.post(url, json=user_data) as response:
                response.raise_for_status()
                body = await response.json()
                new_test_users_ids.append(body["user_id"])
    yield
    with session_factory() as session:
        stmt = delete(User).where(User.id.in_(new_test_users_ids))
        session.execute(stmt)
        session.commit()

