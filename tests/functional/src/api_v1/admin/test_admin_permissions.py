from urllib.parse import urljoin
from http import HTTPStatus

import pytest
from aiohttp import ClientSession

from tests.functional.settings import test_config
from src.db.db import session_factory
from src.db.models import User


@pytest.mark.asyncio
async def test_check_permission(login_test_superuser, create_test_users, create_role):
    test_users = create_test_users
    test_roles = create_role.copy()
    test_roles.sort(key=lambda x: x["position"])
    super_user_data = login_test_superuser
    url = urljoin(test_config.API_BASE_URL, test_config.API_ADMIN_HAS_PERMISSIONS)
    with session_factory() as db_session:
        user = db_session.query(User).get(test_users[0]["user_id"])
        user.role = test_roles[0]["role_name"]
        db_session.commit()
    async with ClientSession(headers={"Authorization": f"Bearer {super_user_data['access_token']}"}) as session:
        async with session.get(url, params={"user_id": test_users[0]["user_id"],
                                            "resource_role_name": test_roles[0]["role_name"]}) as response:
            assert response.ok
    if len(test_roles) > 1:

        async with ClientSession(headers={"Authorization": f"Bearer {super_user_data['access_token']}"}) as session:
            async with session.get(url, params={"user_id": test_users[0]["user_id"],
                                                "resource_role_name": test_roles[-1]["role_name"]}) as response:
                assert response.status == HTTPStatus.FORBIDDEN
