from datetime import datetime, timedelta

import jwt

from schemas.tokens import JWTTokenPair, Token
from core.config import config

JWT_ACCESS_TTL_td = timedelta(minutes=config.JWT_ACCESS_TTL_MINUTES)
JWT_REFRESH_TTL_td = timedelta(days=config.JWT_REFRESH_TTL_DAYS)


class JWTService:
    def __init__(self, user_id: str, user_role: str):
        self.user_id = user_id
        self.user_role = user_role

    def _generate_jwt_access_token(self) -> Token | None:
        iat_utc = datetime.utcnow()
        exp_utc = datetime.utcnow() + timedelta(seconds=JWT_ACCESS_TTL_td.total_seconds())
        payload = {
            "user_id": self.user_id,
            "user_role": self.user_role,
            "exp": exp_utc,
            "iat": iat_utc,
        }
        token = jwt.encode(payload=payload, key=config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
        return Token(token=token, iat_utc=iat_utc, ttl_td=timedelta(seconds=JWT_ACCESS_TTL_td.total_seconds()))

    def _generate_jwt_refresh_token(self) -> Token | None:
        iat_utc = datetime.utcnow()
        exp_utc = datetime.utcnow() + timedelta(seconds=JWT_REFRESH_TTL_td.total_seconds())
        payload = {
            "exp": exp_utc,
            "iat": datetime.utcnow(),
            "user_id": self.user_id,
        }
        token = jwt.encode(payload=payload, key=config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
        return Token(token=token, iat_utc=iat_utc, ttl_td=timedelta(seconds=JWT_REFRESH_TTL_td.total_seconds()))

    def generate_jwt_key_pair(self) -> JWTTokenPair | None:
        jwt_access = self._generate_jwt_access_token()
        jwt_refresh = self._generate_jwt_refresh_token()
        return JWTTokenPair(access_jwt_token=jwt_access, refresh_jwt_token=jwt_refresh)


def get_token_service(user_id: str, user_role: str | None):
    return JWTService(user_id=user_id, user_role=user_role)
