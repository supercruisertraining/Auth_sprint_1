from pydantic import BaseSettings


class TestConfig(BaseSettings):
    API_BASE_URL: str = "http://127.0.0.1:5000"
    API_PATH_CREATE_USER: str = "/api/v1/create_user"
    API_PATH_LOGIN_USER: str = "/api/v1/login"
    API_PATH_UPDATE_USER: str = "/api/v1/update_user"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB_NUM: int = 5

    REDIS_BG_HOST: str = "127.0.0.1"
    REDIS_BG_PORT: int = 6379
    REDIS_BG_DB_NUM: int = 6


test_config = TestConfig()
