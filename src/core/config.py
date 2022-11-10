from enum import Enum
from pydantic import BaseSettings
from urllib.parse import urljoin


class Config(BaseSettings):
    DEBUG: bool = False

    API_BASE: str = "localhost:8888"

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

    JWT_OAUTH2_STATE_SECRET: str = "secret_oauth2"
    JWT_OAUTH2_STATE_TTL_MINUTES: int = 10

    OAUTH2_GOOGLE_REDIRECT_PATH: str = "/auth/google/verification_code"
    OAUTH2_GOOGLE_CLIENT_ID: str = "852912121210-6ddnl8gighlq1ipdjid6mltssn1iu73e.apps.googleusercontent.com"
    OAUTH2_GOOGLE_CLIENT_SECRET: str = "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"
    OAUTH2_GOOGLE_SCOPE: str = "openid email"
    OAUTH2_GOOGLE_DISCOVERY_ENDPOINT: str = "https://accounts.google.com/.well-known/openid-configuration"


config = Config()


class SocialOauthTypeEnum(Enum):
    google = {"redirect_uri": urljoin(f"https://{config.API_BASE}", config.OAUTH2_GOOGLE_REDIRECT_PATH),
              "scope": config.OAUTH2_GOOGLE_SCOPE,
              "discovery_endpoint": config.OAUTH2_GOOGLE_DISCOVERY_ENDPOINT,
              "client_id": config.OAUTH2_GOOGLE_CLIENT_ID,
              "client_secret": config.OAUTH2_GOOGLE_CLIENT_SECRET}
