import json
from abc import ABC, abstractmethod
from functools import lru_cache
from datetime import datetime

from redis import Redis

from core.config import config
from schemas.tokens import Token


class BaseTokenStorage(ABC):

    @abstractmethod
    def push_token(self, user_id: str, token_data: Token):
        pass

    @abstractmethod
    def pop_token(self, token: str) -> str | None:
        pass


class RedisTokenStorage(BaseTokenStorage):

    redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB_NUM)

    def push_token(self, user_id: str, token_data: Token) -> None:
        self.redis.setex(name=token_data.token,
                         time=token_data.ttl_td,
                         value=json.dumps({"exp_utc": str(token_data.iat_utc + token_data.ttl_td),
                                           "user_id": user_id}))

    def pop_token(self, token: str) -> str | None:
        token_data = self.redis.getdel(token)
        if token_data:
            if token_data["exp_utc"] >= datetime.utcnow():
                return token_data["user_id"]
        return None


@lru_cache
def get_token_storage_service():
    return RedisTokenStorage()
