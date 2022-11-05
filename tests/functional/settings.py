from pydantic import BaseSettings


class TestConfig(BaseSettings):
    API_BASE_URL: str = "http://127.0.0.1:5000"
    API_PATH_CREATE_USER: str = "/api/v1/create_user"
    API_PATH_LOGIN_USER: str = "/api/v1/login"
    API_PATH_UPDATE_USER: str = "/api/v1/update_user"
    API_PATH_SOFT_LOGOUT_USER: str = "/api/v1/logout"
    API_PATH_HARD_LOGOUT_USER: str = "/api/v1/logout_hard"
    API_PATH_REFRESH: str = "/api/v1/refresh"
    API_GET_ROLES: str = "/api/v1/get_roles"
    API_ADMIN_LOGIN: str = "/admin/api/v1/login"
    API_ADMIN_LOGOUT: str = "/admin/api/v1/logout"
    API_PATH_ADMIN_REFRESH: str = "/admin/api/v1/refresh"
    API_ADMIN_CREATE_ROLE: str = "/admin/api/v1/create_role"
    API_ADMIN_DELETE_ROLE: str = "/admin/api/v1/delete_role"
    API_ADMIN_ASSIGN_USER_ROLE: str = "/admin/api/v1/assign_role"
    API_ADMIN_UPDATE_ROLE: str = "/admin/api/v1/update_role"
    API_ADMIN_HAS_PERMISSIONS: str = "/admin/api/v1/check_permission"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB_NUM: int = 5

    REDIS_BG_HOST: str = "127.0.0.1"
    REDIS_BG_PORT: int = 6379
    REDIS_BG_DB_NUM: int = 6

    # Для админки
    REDIS_ADMIN_HOST: str = "127.0.0.1"
    REDIS_ADMIN_PORT: int = 6379
    REDIS_ADMIN_DB_NUM: int = 7
    REDIS_ADMIN_BG_HOST: str = "127.0.0.1"
    REDIS_ADMIN_BG_PORT: int = 6379
    REDIS_ADMIN_BG_DB_NUM: int = 8


test_config = TestConfig()
