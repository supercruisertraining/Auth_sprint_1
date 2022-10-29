from pydantic import BaseSettings


class TestConfig(BaseSettings):
    API_BASE_URL: str = "http://127.0.0.1:5000"
    API_PATH_CRETE_USER: str = "/api/v1/create_user"

test_config = TestConfig()
