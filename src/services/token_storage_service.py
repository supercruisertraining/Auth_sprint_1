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
    redis_background = Redis(host=config.REDIS_BG_HOST, port=config.REDIS_BG_PORT, db=config.REDIS_BG_DB_NUM)

    def push_token(self, user_id: str, token_data: Token) -> None:
        self.redis.setex(name=token_data.token,
                         time=token_data.ttl_td,
                         value=json.dumps({"exp_utc": str(token_data.iat_utc + token_data.ttl_td),
                                           "user_id": user_id}))
        self.redis_background.setex(name=self._cook_key_for_background(token=token_data.token, user_id=user_id),
                                    time=token_data.ttl_td,
                                    value=json.dumps({"exp_utc": str(token_data.iat_utc + token_data.ttl_td),
                                                      "user_id": user_id,
                                                      "token": token_data.token}))

    def pop_token(self, token: str) -> str | None:
        token_data = self.redis.getdel(token)
        if token_data:
            token_data = json.loads(token_data)
            exp_utc = datetime.fromisoformat(token_data["exp_utc"])
            if exp_utc >= datetime.utcnow():
                return token_data["user_id"]
        return None

    def get_tokens_from_background(self, user_id: str):
        search_str = self._cook_key_for_background(token="*", user_id=user_id)
        bg_keys_list = self.redis_background.keys(pattern=search_str) or []
        result_list = []
        for bg_key in bg_keys_list:
            bg_token_data_raw = self.redis_background.getdel(bg_key)
            bg_token_data = json.loads(bg_token_data_raw) if bg_token_data_raw else {}
            result_list.append(bg_token_data.get("token", ""))
        return result_list

    def _cook_key_for_background(self, token: str, user_id: str) -> str:
        return config.REDIS_BG_FORMAT_KEY.format(token=token, user_id=user_id)


@lru_cache
def get_token_storage_service():
    return RedisTokenStorage()
