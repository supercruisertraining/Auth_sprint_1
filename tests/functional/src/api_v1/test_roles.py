from urllib.parse import urljoin

import pytest
from aiohttp import ClientSession

from src.db.db import session_factory
from src.db.models import User
from tests.functional.test_data.role_test_data import test_role_names
from tests.functional.settings import test_config


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


@pytest.mark.asyncio
async def test_get_roles(create_role):
    test_roles = create_role
    url = urljoin(test_config.API_BASE_URL, test_config.API_GET_ROLES)
    async with ClientSession() as session:
        # Проверяем негативный случай: попытка присвоения несуществующей роли
        async with session.get(url) as response:
            assert response.ok
            body = await response.json()
    assert isinstance(body, list)
    body = [el["role_name"] for el in body]
    body.sort()
    test_roles.sort()
    assert body == test_roles
