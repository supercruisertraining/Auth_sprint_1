from pydantic import BaseSettings


class Config(BaseSettings):
    DEBUG: bool = False
    DO_TRACE: bool = False
    SENTRY_DSN: str | None = None

    API_BASE: str = "localhost:5000"

    DB_USER: str = "app"
    DB_PASSWORD: str = "123qwe"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "movies_database"
    SCHEMAS_SEARCH_ORDER: str = "auth,content,public"

    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 6831

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

    OAUTH2_GOOGLE_REDIRECT_PATH: str = "/api/v1/auth_social/google/verification_code"
    OAUTH2_GOOGLE_CLIENT_ID: str = "852912121210-6ddnl8gighlq1ipdjid6mltssn1iu73e.apps.googleusercontent.com"
    OAUTH2_GOOGLE_CLIENT_SECRET: str = "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"
    OAUTH2_GOOGLE_SCOPE: str = "openid email"
    OAUTH2_GOOGLE_DISCOVERY_ENDPOINT: str | None = "https://accounts.google.com/.well-known/openid-configuration"
    OAUTH2_GOOGLE_AUTHORIZATION_ENDPOINT: str | None = None
    OAUTH2_GOOGLE_TOKEN_ENDPOINT: str | None = None
    OAUTH2_GOOGLE_USERINFO_ENDPOINT: str | None = None

    OAUTH2_YANDEX_REDIRECT_PATH: str = "/api/v1/auth_social/yandex/verification_code"
    OAUTH2_YANDEX_CLIENT_ID: str = "da38ffcf656d414cb3cb6c5d5448bd3e"
    OAUTH2_YANDEX_CLIENT_SECRET: str = "83770970e2274e48b8a168ac99d447e1"
    OAUTH2_YANDEX_SCOPE: str = "login:email login:info"
    OAUTH2_YANDEX_DISCOVERY_ENDPOINT: str | None = None
    OAUTH2_YANDEX_AUTHORIZATION_ENDPOINT: str | None = "https://oauth.yandex.ru/authorize"
    OAUTH2_YANDEX_TOKEN_ENDPOINT: str | None = "https://oauth.yandex.ru/token"
    OAUTH2_YANDEX_USERINFO_ENDPOINT: str | None = "https://login.yandex.ru/info"


config = Config()
