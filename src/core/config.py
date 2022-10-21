from pydantic import BaseSettings


class Config(BaseSettings):
    DB_USER: str = "app"
    DB_PASSWORD: str = "123qwe"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "movies_database"


config = Config()
