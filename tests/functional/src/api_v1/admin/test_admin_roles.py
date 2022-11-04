import json
import jwt
from urllib.parse import urljoin
from asyncio import sleep
from random import randint

import pytest
from aioredis import Redis
from aiohttp import ClientSession

from tests.functional.settings import test_config
from src.core.config import config
from src.db.db import session_factory
from src.db.models import Role


@pytest.mark.asyncio
async def test_create_role(login_test_superuser):
    new_role_name = "some_new_role"
    super_user_data = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_CREATE_ROLE)
    async with ClientSession(headers={"Authorization": f"Bearer {super_user_data['access_token']}"}) as session:
        async with session.post(url, json={"role_name": new_role_name}) as response:
            assert response.ok
    with session_factory() as db_session:
        role = db_session.query(Role).get(new_role_name)
        assert role
        db_session.delete(role)
        db_session.commit()


@pytest.mark.asyncio
async def test_delete_role(login_test_superuser):
    new_role_name = "some_new_role_2"
    with session_factory() as db_session:
        db_session.add(Role(role_name=new_role_name))
        db_session.commit()

    super_user_data = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_DELETE_ROLE)
    async with ClientSession(headers={"Authorization": f"Bearer {super_user_data['access_token']}"}) as session:
        async with session.delete(url, json={"role_name": new_role_name}) as response:
            assert response.ok
    with session_factory() as db_session:
        role = db_session.query(Role).get(new_role_name)
        assert not role
        if role:
            db_session.delete(role)
            db_session.commit()
