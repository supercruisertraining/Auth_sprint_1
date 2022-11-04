from pydantic import BaseSettings, Field


class Config(BaseSettings):
    DEBUG: bool = False

    DB_USER: str = "app"
    DB_PASSWORD: str = "123qwe"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "movies_database"
    SCHEMAS_SEARCH_ORDER: str = "auth,content,public"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB_NUM: int = 5
    REDIS_BG_HOST: str = "127.0.0.1"
    REDIS_BG_PORT: int = 6379
    REDIS_BG_DB_NUM: int = 6
    REDIS_BG_FORMAT_KEY: str = "{user_id}::{token}"

    # Для админки
    REDIS_ADMIN_HOST: str = "127.0.0.1"
    REDIS_ADMIN_PORT: int = 6379
    REDIS_ADMIN_DB_NUM: int = 7
    REDIS_ADMIN_BG_HOST: str = "127.0.0.1"
    REDIS_ADMIN_BG_PORT: int = 6379
    REDIS_ADMIN_BG_DB_NUM: int = 8

    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MINUTES: int = 5
    JWT_REFRESH_TTL_DAYS: int = 1


config = Config()
