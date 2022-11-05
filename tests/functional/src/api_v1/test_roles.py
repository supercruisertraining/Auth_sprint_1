from urllib.parse import urljoin

import pytest
from aiohttp import ClientSession

from tests.functional.settings import test_config


@pytest.mark.asyncio
async def test_get_roles(create_role):
    test_roles = create_role
    url = urljoin(test_config.API_BASE_URL, test_config.API_GET_ROLES)
    async with ClientSession() as session:
        async with session.get(url) as response:
            assert response.ok
            body = await response.json()
    assert isinstance(body, list)
    body = [el["role_name"] for el in body]
    body.sort()
    test_role_names = [test_role["role_name"] for test_role in test_roles]
    test_role_names.sort()
    assert body == test_role_names
