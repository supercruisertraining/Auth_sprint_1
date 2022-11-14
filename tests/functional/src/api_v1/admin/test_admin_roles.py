from urllib.parse import urljoin
from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.functional.settings import test_config
from src.db.db import session_factory
from src.db.models import Role, User
from tests.functional.test_data.role_test_data import test_roles


@pytest.mark.asyncio
async def test_create_role(login_test_superuser):
    new_role = {"role_name": "some_new_role", "position": 100}
    super_user_data = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_CREATE_ROLE)
    async with ClientSession(headers={"Authorization": f"Bearer {super_user_data['access_token']}",
                                      "X-Request_id": str(uuid4())}) as session:
        async with session.post(url, json=new_role) as response:
            assert response.ok
    with session_factory() as db_session:
        role = db_session.query(Role).get(new_role["role_name"])
        assert role
        db_session.delete(role)
        db_session.commit()


@pytest.mark.asyncio
async def test_delete_role(login_test_superuser):
    new_role = {"role_name": "some_new_role_2", "position": 200}
    with session_factory() as db_session:
        db_session.add(Role(role_name=new_role["role_name"], position=new_role["position"]))
        db_session.commit()

    super_user_data = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_DELETE_ROLE)
    async with ClientSession(headers={"Authorization": f"Bearer {super_user_data['access_token']}",
                                      "X-Request_id": str(uuid4())}) as session:
        async with session.delete(url, json={"role_name": new_role["role_name"]}) as response:
            assert response.ok
    with session_factory() as db_session:
        role = db_session.query(Role).get(new_role["role_name"])
        assert not role
        if role:
            db_session.delete(role)
            db_session.commit()


@pytest.mark.asyncio
async def test_update_role(login_test_superuser):
    new_role = {"role_name": "some_new_role_2", "position": 200}
    with session_factory() as db_session:
        db_session.add(Role(role_name=new_role["role_name"], position=new_role["position"]))
        db_session.commit()

    super_user_data = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_UPDATE_ROLE)
    async with ClientSession(headers={"Authorization": f"Bearer {super_user_data['access_token']}",
                                      "X-Request_id": str(uuid4())}) as session:
        async with session.patch(url, json={"role_name": new_role["role_name"],
                                            "role_description": "test description",
                                            "position": 201}) as response:
            assert response.ok
    with session_factory() as db_session:
        role = db_session.query(Role).get(new_role["role_name"])
        assert role.description == "test description"
        assert role.position == 201
        db_session.delete(role)
        db_session.commit()


@pytest.mark.asyncio
async def test_assign_role(login_test_superuser, create_test_users):
    test_users = create_test_users
    super_user = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_ASSIGN_USER_ROLE)
    not_existing_role_name = {"role_name": "not_existing_role", "position": 300}
    async with ClientSession(headers={"Authorization": f"Bearer {super_user['access_token']}",
                                      "X-Request_id": str(uuid4())}) as session:

        # Проверяем негативный случай: попытка присвоения несуществующей роли
        async with session.patch(url, json={"role_name": not_existing_role_name,
                                            "user_id": test_users[0]["user_id"]}) as response:
            assert not response.ok
        with session_factory() as db_session:
            user_obj = db_session.query(User).get(test_users[0]["user_id"])
            assert user_obj.role != not_existing_role_name

        async with session.patch(url, json={"role_name": test_roles[0]["role_name"],
                                            "user_id": test_users[0]["user_id"]}) as response:
            assert response.ok
        with session_factory() as db_session:
            user_obj = db_session.query(User).get(test_users[0]["user_id"])
            assert user_obj.role == test_roles[0]["role_name"]
